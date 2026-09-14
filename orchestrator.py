import sys
import os
import time
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def _load_env_file():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip("'\""))

_load_env_file()

if not os.environ.get("GROQ_API_KEY"):
    raise SystemExit(
        "\n[ERROR] Missing environment variable: GROQ_API_KEY\n\n"
        "  Get a free key at https://console.groq.com -> API Keys\n"
        "  Then set it before running:\n\n"
        "  PowerShell:  $env:GROQ_API_KEY='your_key_here'\n"
        "  CMD:         set GROQ_API_KEY=your_key_here\n"
    )

from strands import Agent, tool
from model import get_model

from agents.finance_agent import run_finance_query
from agents.ops_agent import run_ops_query
from agents.marketing_agent import run_marketing_query

_call_count = {"n": 0}
_last_run_details = {
    "specialists_called": [],
    "specialist_results": {
        "finance": {"called": False, "summary": ""},
        "ops": {"called": False, "summary": ""},
        "marketing": {"called": False, "summary": ""},
    },
}


def _call_with_ratelimit_retry(fn, *args, **kwargs):
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            err_msg = f"{str(e)} {getattr(e, '__cause__', '')} {repr(e)}"
            is_ratelimit = any(w in err_msg.lower() for w in ["rate limit", "ratelimit", "429", "eventloop"])
            if is_ratelimit and attempt < max_attempts:
                match = re.search(r"try again in ([0-9.]+)s", err_msg, re.IGNORECASE)
                if not match:
                    match = re.search(r"in ([0-9.]+)s", err_msg, re.IGNORECASE)
                wait_sec = float(match.group(1)) + 1.0 if match else 6.0
                print(f"  [!] Rate limit reached. Auto-retrying in {wait_sec:.1f}s (Attempt {attempt}/{max_attempts})...")
                time.sleep(wait_sec)
            else:
                raise


def _timed_specialist(name: str, fn, query: str) -> str:
    _call_count["n"] += 1
    if _call_count["n"] > 1:
        wait = 1
        time.sleep(wait)
    print(f"\n  [>>] [Orchestrator] -> {name} specialist")
    result = _call_with_ratelimit_retry(fn, query)
    print(f"  [OK] [Orchestrator] <- {name} specialist responded")

    key = name.lower()
    if key not in _last_run_details["specialists_called"]:
        _last_run_details["specialists_called"].append(key)
    _last_run_details["specialist_results"][key] = {
        "called": True,
        "summary": result,
    }
    return result


@tool
def finance_specialist(query: str) -> str:
    """Handles revenue, sales trends, forecasts, and anomaly questions."""
    return _timed_specialist("FINANCE", run_finance_query, query)


@tool
def ops_specialist(query: str) -> str:
    """Handles team status, blocked items, scheduling, and email draft requests."""
    return _timed_specialist("OPS", run_ops_query, query)


@tool
def marketing_specialist(query: str) -> str:
    """Handles campaign performance, CTR, conversion rates, and ad spend questions."""
    return _timed_specialist("MARKETING", run_marketing_query, query)


orchestrator = Agent(
    model=get_model(),
    system_prompt=(
        "You are Chief of Staff. Call all 3 specialist tools (finance_specialist, ops_specialist, marketing_specialist) to gather data.\n"
        "Synthesize their reports into a concise briefing:\n"
        "- Finance: 1-2 bullet points\n"
        "- Operations: 1-2 bullet points\n"
        "- Marketing: 1-2 bullet points\n"
        "- Key Actions: 3 numbered actions\n"
        "Keep the full response under 150 words."
    ),
    tools=[finance_specialist, ops_specialist, marketing_specialist],
)

SAMPLE_QUERY = (
    "Give me this week's briefing: revenue trend, pending ops items, "
    "and how our last campaign performed."
)


def run_briefing(query: str) -> str:
    _call_count["n"] = 0
    _last_run_details["specialists_called"] = []
    _last_run_details["specialist_results"] = {
        "finance": {"called": False, "summary": ""},
        "ops": {"called": False, "summary": ""},
        "marketing": {"called": False, "summary": ""},
    }

    print(f"\n{'='*70}")
    print("AGentic Resolve -- Business Briefing")
    print(f"{'='*70}")
    print(f"Query: {query}")
    print(f"{'-'*70}")
    print("[Orchestrator] Analysing and delegating to specialists...\n")

    response = str(_call_with_ratelimit_retry(orchestrator, query))

    print(f"\n{'='*70}")
    print("SYNTHESIZED BRIEFING")
    print(f"{'='*70}")
    print(response)
    print(f"{'='*70}\n")
    return response


def run_briefing_structured(query: str) -> dict:
    response = run_briefing(query)
    return {
        "query": query,
        "specialists_called": list(_last_run_details["specialists_called"]),
        "specialist_results": dict(_last_run_details["specialist_results"]),
        "synthesized_briefing": response,
    }


if __name__ == "__main__":
    run_briefing(SAMPLE_QUERY)
