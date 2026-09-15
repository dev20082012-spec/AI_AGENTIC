import os
import sys
import time
import re
import json
from typing import Generator
import requests
import litellm

def _load_env():
    """Load .env file for local dev. Production platforms inject env vars natively."""
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=False)
    except ImportError:
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip().strip("'\""))

_load_env()

# ── Provider & Model Settings ────────────────────────────────────────────────
PRIMARY_PROVIDER = os.environ.get("PRIMARY_PROVIDER", "groq").strip().lower()
PRIMARY_MODEL = os.environ.get("PRIMARY_MODEL", "qwen/qwen3.8-27b").strip()

FALLBACK_PROVIDER = os.environ.get("FALLBACK_PROVIDER", "openrouter").strip().lower()
FALLBACK_MODEL = os.environ.get("FALLBACK_MODEL", "poolside/laguna-s-2.1:free").strip()

# OpenRouter native model fallback list (ordered by priority)
_raw_or_models = os.environ.get("OPENROUTER_FALLBACK_MODELS", f"{FALLBACK_MODEL},openrouter/auto")
OPENROUTER_FALLBACK_MODELS = [m.strip() for m in _raw_or_models.split(",") if m.strip()]

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

litellm.num_retries = 3
litellm.drop_params = True


def _check_env(var: str, hint: str = ""):
    val = os.environ.get(var)
    if not val:
        raise RuntimeError(
            f"Missing required environment variable: {var}. {hint}"
        )
    return val


class TransientProviderError(Exception):
    """Raised when a model provider hits a rate limit (429) or transient 5xx."""
    pass


def _clean_content(text: str) -> str:
    """Strips chain-of-thought, thinking tokens, and hidden reasoning tags cleanly."""
    if not text:
        return ""
    if "<think>" in text:
        if "</think>" in text:
            text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
        else:
            text = re.sub(r"^<think>\s*", "", text)
    return text.strip()


def _call_groq(
    messages: list[dict],
    model: str = None,
    max_tokens: int = 450,
    temperature: float = 0.3,
) -> tuple[str, str]:
    groq_key = _check_env("GROQ_API_KEY", "Add GROQ_API_KEY to your backend .env file")
    primary_target = model or PRIMARY_MODEL

    # If primary target is qwen3.8, allow qwen3.6 as same-provider capacity fallback on 429
    models_to_try = [primary_target]
    if primary_target == "qwen/qwen3.8-27b":
        models_to_try.append("qwen/qwen3.6-27b")

    headers = {
        "Authorization": f"Bearer {groq_key}",
        "Content-Type": "application/json",
    }

    last_err = None
    for target_model in models_to_try:
        payload = {
            "model": target_model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=25)
        except requests.exceptions.RequestException as e:
            last_err = str(e)
            continue

        if resp.status_code == 200:
            data = resp.json()
            msg = data.get("choices", [{}])[0].get("message", {})
            content = (msg.get("content") or msg.get("reasoning") or "").strip()
            if content:
                return content, target_model

        # Strictly do not retry client/auth errors
        if resp.status_code in (401, 403, 400):
            resp.raise_for_status()

        err_text = resp.text[:250]
        last_err = f"Groq HTTP {resp.status_code}: {err_text}"
        continue

    raise TransientProviderError(last_err or "All Groq models failed")


def _call_openrouter(
    messages: list[dict],
    model: str = None,
    max_tokens: int = 400,
    temperature: float = 0.3,
) -> tuple[str, str]:
    or_key = _check_env("OPENROUTER_API_KEY", "Add OPENROUTER_API_KEY to your backend .env file")
    target_model = (model or FALLBACK_MODEL).strip()
    if target_model.startswith("openrouter/"):
        target_model = target_model[len("openrouter/"):]

    # Use native OpenRouter models array fallback
    models_list = [target_model]
    for m in OPENROUTER_FALLBACK_MODELS:
        clean_m = m[len("openrouter/"):] if m.startswith("openrouter/") else m
        if clean_m not in models_list:
            models_list.append(clean_m)

    headers = {
        "Authorization": f"Bearer {or_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://agentic-resolve.local",
        "X-Title": "AGentic Resolve Executive AI",
    }

    payload = {
        "model": models_list[0],
        "models": models_list,  # Native OpenRouter ordered model fallback
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    try:
        resp = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=35)
    except requests.exceptions.RequestException as e:
        raise TransientProviderError(f"OpenRouter connection error: {e}")

    if resp.status_code == 200:
        data = resp.json()
        model_used = data.get("model", models_list[0])
        msg = data.get("choices", [{}])[0].get("message", {})
        content = (msg.get("content") or msg.get("reasoning") or "").strip()
        if content:
            return content, model_used
        raise TransientProviderError("OpenRouter returned empty content")

    if resp.status_code in (401, 403, 400):
        resp.raise_for_status()

    raise TransientProviderError(f"OpenRouter HTTP {resp.status_code}: {resp.text[:200]}")


def chat_completion(
    messages: list[dict],
    model: str = None,
    max_tokens: int = 450,
    temperature: float = 0.3,
    return_meta: bool = False,
):
    """
    Executes a chat completion with transparent, resilient failover.
    Attempts PRIMARY_PROVIDER (default: Groq).
    If 429 or transient provider error occurs, automatically fails over to
    FALLBACK_PROVIDER (default: OpenRouter) using native ordered model fallback.
    """
    start_time = time.time()
    primary_err = None
    provider_used = PRIMARY_PROVIDER
    model_used = model or PRIMARY_MODEL
    fallback_used = False

    # 1. Try Primary Provider (Groq)
    try:
        if PRIMARY_PROVIDER == "groq":
            res, model_used = _call_groq(messages, model=model, max_tokens=max_tokens, temperature=temperature)
            res = _clean_content(res)
            latency_ms = int((time.time() - start_time) * 1000)
            meta = {
                "provider": provider_used,
                "model": model_used,
                "fallback_used": False,
                "latency_ms": latency_ms,
            }
            return (res, meta) if return_meta else res
        elif PRIMARY_PROVIDER == "openrouter":
            res, model_used = _call_openrouter(messages, model=model, max_tokens=max_tokens, temperature=temperature)
            res = _clean_content(res)
            latency_ms = int((time.time() - start_time) * 1000)
            meta = {
                "provider": provider_used,
                "model": model_used,
                "fallback_used": False,
                "latency_ms": latency_ms,
            }
            return (res, meta) if return_meta else res
    except (TransientProviderError, requests.exceptions.RequestException) as e:
        primary_err = e
        print(f"  [!] Primary provider ({PRIMARY_PROVIDER}) transient error: {e}. Activating fallback...")

    # 2. Try Fallback Provider (OpenRouter)
    if FALLBACK_PROVIDER and os.environ.get("OPENROUTER_API_KEY"):
        try:
            fallback_used = True
            provider_used = FALLBACK_PROVIDER
            if FALLBACK_PROVIDER == "openrouter":
                res, model_used = _call_openrouter(messages, model=FALLBACK_MODEL, max_tokens=max_tokens, temperature=temperature)
            else:
                res, model_used = _call_groq(messages, model=PRIMARY_MODEL, max_tokens=max_tokens, temperature=temperature)
            res = _clean_content(res)
            latency_ms = int((time.time() - start_time) * 1000)
            meta = {
                "provider": provider_used,
                "model": model_used,
                "fallback_used": True,
                "latency_ms": latency_ms,
            }
            return (res, meta) if return_meta else res
        except Exception as fb_err:
            raise RuntimeError(
                f"Both primary ({PRIMARY_PROVIDER}: {primary_err}) and fallback ({FALLBACK_PROVIDER}: {fb_err}) failed."
            ) from fb_err

    if primary_err:
        raise primary_err
    raise RuntimeError(f"Unknown provider '{PRIMARY_PROVIDER}' configured.")


def stream_chat_completion(
    messages: list[dict],
    model: str = None,
    max_tokens: int = 450,
    temperature: float = 0.3,
) -> Generator[str, None, dict]:
    """
    Streams completion tokens chunk by chunk.
    Falls back gracefully if streaming is interrupted.
    Yields string deltas, and the return value or final chunk carries metadata.
    """
    groq_key = os.environ.get("GROQ_API_KEY")
    or_key = os.environ.get("OPENROUTER_API_KEY")
    start_time = time.time()

    # Try Groq streaming first if Groq key available
    if PRIMARY_PROVIDER == "groq" and groq_key:
        headers = {
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model or PRIMARY_MODEL,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
        }
        try:
            resp = requests.post(GROQ_API_URL, headers=headers, json=payload, stream=True, timeout=20)
            if resp.status_code == 200:
                inside_think = False
                for line in resp.iter_lines():
                    if not line:
                        continue
                    line_str = line.decode("utf-8", errors="replace")
                    if line_str.startswith("data: "):
                        data_str = line_str[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if not delta:
                                continue
                            if "<think>" in delta:
                                inside_think = True
                                delta = delta.split("<think>")[0]
                            if "</think>" in delta:
                                inside_think = False
                                delta = delta.split("</think>")[-1]
                            if not inside_think and delta:
                                yield delta
                        except Exception:
                            continue
                return
        except Exception as e:
            print(f"  [!] Groq stream failed ({e}), attempting non-streaming fallback...")

    # Fallback to non-streaming chat_completion yielding the full response
    full_text, meta = chat_completion(messages, model=model, max_tokens=max_tokens, temperature=temperature, return_meta=True)
    # Split cleanly into tokens/words for progressive display
    words = full_text.split(" ")
    for i, word in enumerate(words):
        yield word + (" " if i < len(words) - 1 else "")
        time.sleep(0.015)


def get_model():
    """Returns a model instance compatible with the Strands Agents SDK."""
    try:
        from strands.models.litellm import LiteLLMModel
    except ImportError:
        raise SystemExit(
            "\n[ERROR] LiteLLM provider not installed.\n"
            "  Run: pip install 'strands-agents[litellm]' litellm\n"
        )

    _check_env(
        "GROQ_API_KEY",
        "Get a free key at https://console.groq.com -> API Keys"
    )

    return LiteLLMModel(
        model_id=f"groq/{PRIMARY_MODEL}" if not PRIMARY_MODEL.startswith("groq/") else PRIMARY_MODEL,
        params={
            "temperature": 0.2,
            "max_tokens": 380,
        },
    )
