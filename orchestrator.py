import sys
import os
import time

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


def _timed_specialist(name: str, fn, query: str) -> str:
    _call_count["n"] += 1
    if _call_count["n"] > 1:
        wait = 30
        print(f"  [..] Pausing {wait}s to stay within API rate limits...")
        time.sleep(wait)
    print(f"\n  [>>] [Orchestrator] -> {name} specialist")
    result = fn(query)
    print(f"  [OK] [Orchestrator] <- {name} specialist responded")
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
        "You are Chief of Staff. Call the right specialist(s) then write ONE concise briefing.\n"
        "- finance_specialist: revenue, sales, forecasts, anomalies\n"
        "- ops_specialist: team tasks, blockers, scheduling\n"
        "- marketing_specialist: campaigns, CTR, ad performance\n"
        "Use real numbers from specialist responses. End with 3 Key Actions."
    ),
    tools=[finance_specialist, ops_specialist, marketing_specialist],
)

SAMPLE_QUERY = (
    "Give me this week's briefing: revenue trend, pending ops items, "
    "and how our last campaign performed."
)


def run_briefing(query: str) -> str:
    _call_count["n"] = 0
    print(f"\n{'='*70}")
    print("AGentic Resolve -- Business Briefing")
    print(f"{'='*70}")
    print(f"Query: {query}")
    print(f"{'-'*70}")
    print("[Orchestrator] Analysing and delegating to specialists...\n")

    response = str(orchestrator(query))

    print(f"\n{'='*70}")
    print("SYNTHESIZED BRIEFING")
    print(f"{'='*70}")
    print(response)
    print(f"{'='*70}\n")
    return response


if __name__ == "__main__":
    run_briefing(SAMPLE_QUERY)
