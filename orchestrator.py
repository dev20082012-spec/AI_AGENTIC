"""
AGentic Resolve — Executive Business Briefing Orchestrator

Coordinates Finance, Operations, and Marketing specialist analyses for full
executive business briefings. Handles partial specialist failures gracefully,
ensuring uninterrupted synthesis across available data without fabricating missing numbers.
"""

import sys
import os
import time
from datetime import datetime, timezone
import re
from model import chat_completion, get_model
from agents.finance_agent import run_finance_query_structured
from agents.ops_agent import run_ops_query_structured
from agents.marketing_agent import run_marketing_query_structured

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BRIEFING_SYNTHESIS_SYSTEM_PROMPT = (
    "You are the Executive Chief of Staff delivering a comprehensive, high-impact Business Briefing "
    "for executive leadership. Synthesize the findings from Finance, Operations, and Marketing into a "
    "decision-ready intelligence report.\n\n"
    "Structure your response clearly with these sections:\n"
    "### Executive Summary\n"
    "- 2-3 sentences summarizing the cross-departmental business trajectory.\n\n"
    "### Key Department Findings\n"
    "- **Finance**: Core revenue metrics, product momentum, and forecasts.\n"
    "- **Operations**: Workflow velocity, blocked initiatives, and staffing bottlenecks.\n"
    "- **Marketing**: Conversion ROI, top customer segments, and regional performance.\n\n"
    "### Critical Risks & Vulnerabilities\n"
    "- Bulleted list of top risks across departments requiring executive mitigation.\n\n"
    "### Strategic Opportunities\n"
    "- High-ROI levers to accelerate growth or eliminate bottlenecks.\n\n"
    "### Top 3 Recommended Actions\n"
    "1. [Action 1: Immediate operational or financial priority]\n"
    "2. [Action 2: Growth or campaign optimization]\n"
    "3. [Action 3: Structural or risk-prevention measure]\n\n"
    "CRITICAL RULES:\n"
    "1. Never invent or hallucinate metrics. Use ONLY verified data from the specialist reports.\n"
    "2. If a specialist is unavailable, state that department's data is temporarily offline and DO NOT fabricate it.\n"
    "3. Be direct, authoritative, and focused on executive decisions."
)

SAMPLE_QUERY = (
    "Give me this week's briefing: revenue trend, pending ops items, "
    "and how our last campaign performed."
)


def _extract_section_items(text: str, heading_pattern: str) -> list[str]:
    """Extracts bulleted or numbered items from a specific markdown section."""
    items = []
    pattern = rf"###\s*{heading_pattern}.*?\n(.*?)(?=\n###|\Z)"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        section_body = match.group(1).strip()
        for line in section_body.split("\n"):
            line = line.strip()
            # Strip bullet or number prefix
            cleaned = re.sub(r"^([*•\-]|\d+\.)\s*", "", line).strip()
            if cleaned and not cleaned.startswith("#"):
                items.append(cleaned)
    return items


def run_briefing_structured(query: str) -> dict:
    """
    Executes a structured executive briefing across all 3 specialist domains:
    1. Validates input query.
    2. Runs Finance, Operations, and Marketing analyses in isolated try/except blocks.
    3. Records per-specialist status ('consulted' vs 'unavailable').
    4. Synthesizes findings using centralized chat_completion with fallback resilience.
    5. Returns structured results including key risks, opportunities, and top actions.
    """
    start_time = time.time()
    query = query.strip() if query else SAMPLE_QUERY

    print(f"\n{'='*75}")
    print("AGENTIC RESOLVE — FULL BUSINESS BRIEFING")
    print(f"Query: {query}")
    print(f"{'-'*75}")

    specialists_called = []
    specialist_results = {
        "finance": {"called": False, "status": "skipped", "summary": "", "metrics": {}, "findings": []},
        "ops": {"called": False, "status": "skipped", "summary": "", "metrics": {}, "findings": []},
        "marketing": {"called": False, "status": "skipped", "summary": "", "metrics": {}, "findings": []},
    }

    # 1. Finance Analysis
    print("  [>>] Consulting Finance Specialist...")
    try:
        f_data = run_finance_query_structured(query)
        specialist_results["finance"] = {
            "called": True,
            "status": "consulted",
            "summary": f_data.get("answer", ""),
            "findings": f_data.get("findings", []),
            "metrics": f_data.get("metrics", {}),
            "warnings": f_data.get("warnings", []),
            "recommendations": f_data.get("recommendations", []),
        }
        specialists_called.append("finance")
        print("  [OK] Finance analysis complete")
    except Exception as e:
        print(f"  [!] Finance specialist failed: {e}")
        specialist_results["finance"] = {
            "called": True,
            "status": "unavailable",
            "summary": "Finance specialist temporarily unavailable.",
            "error": str(e),
            "findings": [],
            "metrics": {},
            "warnings": [],
            "recommendations": [],
        }

    # 2. Operations Analysis
    print("  [>>] Consulting Operations Specialist...")
    try:
        o_data = run_ops_query_structured(query)
        specialist_results["ops"] = {
            "called": True,
            "status": "consulted",
            "summary": o_data.get("answer", ""),
            "findings": o_data.get("findings", []),
            "metrics": o_data.get("metrics", {}),
            "warnings": o_data.get("warnings", []),
            "recommendations": o_data.get("recommendations", []),
        }
        specialists_called.append("ops")
        print("  [OK] Operations analysis complete")
    except Exception as e:
        print(f"  [!] Operations specialist failed: {e}")
        specialist_results["ops"] = {
            "called": True,
            "status": "unavailable",
            "summary": "Operations specialist temporarily unavailable.",
            "error": str(e),
            "findings": [],
            "metrics": {},
            "warnings": [],
            "recommendations": [],
        }

    # 3. Marketing Analysis
    print("  [>>] Consulting Marketing Specialist...")
    try:
        m_data = run_marketing_query_structured(query)
        specialist_results["marketing"] = {
            "called": True,
            "status": "consulted",
            "summary": m_data.get("answer", ""),
            "findings": m_data.get("findings", []),
            "metrics": m_data.get("metrics", {}),
            "warnings": m_data.get("warnings", []),
            "recommendations": m_data.get("recommendations", []),
        }
        specialists_called.append("marketing")
        print("  [OK] Marketing analysis complete")
    except Exception as e:
        print(f"  [!] Marketing specialist failed: {e}")
        specialist_results["marketing"] = {
            "called": True,
            "status": "unavailable",
            "summary": "Marketing specialist temporarily unavailable.",
            "error": str(e),
            "findings": [],
            "metrics": {},
            "warnings": [],
            "recommendations": [],
        }

    # 4. Construct Synthesis Context from available specialists
    context_blocks = []
    for s_name in ("finance", "ops", "marketing"):
        info = specialist_results[s_name]
        if info["status"] == "consulted":
            context_blocks.append(f"=== {s_name.upper()} REPORT ===")
            context_blocks.append(info["summary"])
            if info.get("warnings"):
                context_blocks.append(f"Alerts: {'; '.join(info['warnings'])}")
            if info.get("recommendations"):
                context_blocks.append(f"Recommendations: {'; '.join(info['recommendations'])}")
        else:
            context_blocks.append(
                f"=== {s_name.upper()} REPORT ===\n"
                f"[STATUS: UNAVAILABLE - Data temporarily offline. Do not invent {s_name} data.]"
            )

    synth_messages = [
        {"role": "system", "content": BRIEFING_SYNTHESIS_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Executive Briefing Request: {query}\n\n"
                f"{chr(10).join(context_blocks)}\n\n"
                "Synthesize the available evidence into the executive briefing following the required sections."
            ),
        },
    ]

    print("  [>>] Synthesizing executive briefing...")
    synthesis_text, meta = chat_completion(
        synth_messages,
        max_tokens=650,
        temperature=0.25,
        return_meta=True,
    )
    print("  [OK] Synthesis complete")

    # Extract structured highlights
    key_risks = _extract_section_items(synthesis_text, "Critical Risks")
    key_opportunities = _extract_section_items(synthesis_text, "Strategic Opportunities")
    top_actions = _extract_section_items(synthesis_text, "Top 3 Recommended Actions")

    # Fallback to specialist warnings / recommendations if section parsing yielded empty
    if not key_risks:
        for s in specialist_results.values():
            key_risks.extend(s.get("warnings", []))
    if not top_actions:
        for s in specialist_results.values():
            top_actions.extend(s.get("recommendations", []))

    total_latency_ms = int((time.time() - start_time) * 1000)
    meta["total_latency_ms"] = total_latency_ms

    return {
        "query": query,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "specialists_called": specialists_called,
        "specialist_results": specialist_results,
        "key_risks": key_risks[:4],
        "key_opportunities": key_opportunities[:4],
        "top_actions": top_actions[:3],
        "synthesized_briefing": synthesis_text,
        "metadata": meta,
    }


def run_briefing(query: str) -> str:
    """Backwards-compatible string helper."""
    data = run_briefing_structured(query)
    return data["synthesized_briefing"]


if __name__ == "__main__":
    res = run_briefing_structured(SAMPLE_QUERY)
    print("\n" + "=" * 75)
    print(res["synthesized_briefing"])
    print("=" * 75)
