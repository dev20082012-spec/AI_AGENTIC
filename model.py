import os
import sys
import time
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

BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-5-20251001-v1:0").strip()
BEDROCK_REGION = os.environ.get("BEDROCK_REGION", "us-west-2").strip()

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

litellm.num_retries = 6
litellm.drop_params = True


def _check_env(var: str, hint: str = ""):
    val = os.environ.get(var)
    if not val:
        raise RuntimeError(
            f"Missing required environment variable: {var}. {hint}"
        )
    return val


def _call_groq(messages: list[dict], model: str = None, max_tokens: int = 400, temperature: float = 0.3) -> str:
    groq_key = _check_env("GROQ_API_KEY", "Add GROQ_API_KEY to your backend .env file")
    primary_target = model or PRIMARY_MODEL
    # Multi-model pool on Groq: if qwen3.8 hits OTPM, immediately try qwen3.6
    models_to_try = [primary_target]
    for alt in ["qwen/qwen3.6-27b", "openai/gpt-oss-120b"]:
        if alt not in models_to_try:
            models_to_try.append(alt)

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

        for attempt in range(1, 3):
            try:
                resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
            except Exception as e:
                last_err = str(e)
                continue

            if resp.status_code == 200:
                data = resp.json()
                msg = data.get("choices", [{}])[0].get("message", {})
                content = (msg.get("content") or msg.get("reasoning") or "").strip()
                if content:
                    return content

            err_text = resp.text[:250]
            last_err = f"Groq error HTTP {resp.status_code}: {err_text}"

            if resp.status_code == 429 and attempt == 1:
                import re
                m_ms = re.search(r"in (\d+)ms", err_text)
                m_s = re.search(r"in ([\d.]+)s", err_text)
                wait_s = 1.0
                if m_ms:
                    wait_s = (float(m_ms.group(1)) / 1000.0) + 0.3
                elif m_s:
                    wait_s = float(m_s.group(1)) + 0.5
                time.sleep(min(max(wait_s, 0.5), 3.5))
                continue

            # On persistent 429 or 5xx, break inner loop to try next Groq model
            break

    raise TransientProviderError(last_err or "All Groq models failed")


def _call_openrouter(messages: list[dict], model: str = None, max_tokens: int = 350, temperature: float = 0.3) -> str:
    or_key = _check_env("OPENROUTER_API_KEY", "Add OPENROUTER_API_KEY to your backend .env file")
    primary_model = model or FALLBACK_MODEL
    models_to_try = [primary_model]
    for alt in ["nvidia/nemotron-3.5-lightning:free", "liquid/lfm-2.5-2.6b:free", "openrouter/auto"]:
        if alt not in models_to_try:
            models_to_try.append(alt)

    headers = {
        "Authorization": f"Bearer {or_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://agentic-resolve.local",
        "X-Title": "AGentic Resolve Executive AI",
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
            resp = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                msg = data.get("choices", [{}])[0].get("message", {})
                content = (msg.get("content") or msg.get("reasoning") or "").strip()
                if content:
                    return content
                last_err = f"Model {target_model} returned empty content"
                continue
            last_err = f"Model {target_model} HTTP {resp.status_code}: {resp.text[:120]}"
        except Exception as e:
            last_err = str(e)
            continue

    raise RuntimeError(f"All OpenRouter models failed. Last: {last_err}")


class TransientProviderError(Exception):
    """Raised when a model provider hits a rate limit (429) or transient 5xx."""
    pass


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
    If a rate limit (429) or transient provider error occurs, automatically
    fails over to FALLBACK_PROVIDER (default: OpenRouter) safely.
    """
    primary_err = None
    provider_used = PRIMARY_PROVIDER

    # 1. Try Primary Provider
    try:
        if PRIMARY_PROVIDER == "groq":
            res = _call_groq(messages, model=model, max_tokens=max_tokens, temperature=temperature)
            return (res, provider_used) if return_meta else res
        elif PRIMARY_PROVIDER == "openrouter":
            res = _call_openrouter(messages, model=model, max_tokens=max_tokens, temperature=temperature)
            return (res, provider_used) if return_meta else res
    except (TransientProviderError, requests.exceptions.RequestException) as e:
        primary_err = e
        print(f"  [!] Primary provider ({PRIMARY_PROVIDER}) transient error: {e}. Attempting fallback...")

    # 2. Try Fallback Provider (OpenRouter or Groq alternate)
    if FALLBACK_PROVIDER and os.environ.get("OPENROUTER_API_KEY"):
        try:
            provider_used = FALLBACK_PROVIDER
            print(f"  [>>] Failover activated -> using {FALLBACK_PROVIDER} ({FALLBACK_MODEL})")
            if FALLBACK_PROVIDER == "openrouter":
                res = _call_openrouter(messages, model=FALLBACK_MODEL, max_tokens=max_tokens, temperature=temperature)
            else:
                res = _call_groq(messages, model=PRIMARY_MODEL, max_tokens=max_tokens, temperature=temperature)
            return (res, provider_used) if return_meta else res
        except Exception as fb_err:
            raise RuntimeError(
                f"Both primary ({PRIMARY_PROVIDER}: {primary_err}) and fallback ({FALLBACK_PROVIDER}: {fb_err}) failed."
            ) from fb_err

    # If no fallback is configured or available, re-raise primary error
    if primary_err:
        raise primary_err
    raise RuntimeError(f"Unknown provider '{PRIMARY_PROVIDER}' configured.")


def get_model():
    """Returns a model instance compatible with the Strands Agents SDK."""
    if PRIMARY_PROVIDER == "groq":
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

    elif PRIMARY_PROVIDER == "bedrock":
        try:
            import boto3
            session = boto3.session.Session()
            creds = session.get_credentials()
            if creds is None or creds.resolve() is None:
                raise RuntimeError("No AWS credentials found for Bedrock.")
        except Exception as e:
            raise RuntimeError(f"AWS credential check failed: {e}") from e

        from strands.models import BedrockModel
        return BedrockModel(
            model_id=BEDROCK_MODEL_ID,
            region_name=BEDROCK_REGION,
        )

    else:
        raise RuntimeError(f"Unknown PROVIDER '{PRIMARY_PROVIDER}' in model.py.")
