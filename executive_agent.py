import os
import json
import re
from model import chat_completion
from agents.finance_agent import run_finance_query_structured
from agents.ops_agent import run_ops_query_structured
from agents.marketing_agent import run_marketing_query_structured

MAX_AGENT_STEPS = 5

CHIEF_OF_STAFF_SYNTHESIS_PROMPT = (
    "You are the Executive Chief of Staff for a growing software company. "
    "You communicate clearly, strategically, and concisely with executives. "
    "You have consulted domain specialists (Finance, Operations, Marketing) as needed. "
    "Synthesize the specialist findings and conversation history into a natural, conversational response. "
    "Do NOT force a rigid template. Speak directly to the user's specific question. "
    "Highlight actionable insights, real metrics from the specialist reports, and strategic implications. "
    "Never hallucinate numbers that were not provided by the specialists. "
    "Keep your tone professional, authoritative, yet approachable."
)

ROUTER_PROMPT = """You are the Dispatcher & Intent Analyzer for an Executive Chief of Staff AI.
You receive the user's current message and prior conversation history.

Your job is to decide:
1. Is the message AMBIGUOUS ACROSS DOMAINS and requires clarification?
   ONLY trigger clarification if the request does NOT specify a business domain at all (for example: "Show me performance" or "Give me an update", where it is completely unclear whether the user means sales, ops tasks, or marketing campaigns).
   Do NOT ask clarification if the domain is clear. If the user mentions "sales", "revenue", "products", "money", or "growth", route directly to "finance"! If they mention "tasks", "blocked", "tickets", route to "ops"! If they mention "campaigns", "CTR", "ads", route to "marketing"!
2. If NOT ambiguous, which domain specialists are strictly relevant?
   Options:
   - "finance": revenue, sales trends, products (AlphaApp, BetaSuite), forecasts, financial anomalies.
   - "ops": tasks, blocked items, stale work, team bottlenecks, scheduling, tickets, roadmaps.
   - "marketing": ad campaigns, CTR, conversions, demographics, regions, ad spend.
3. If the user asks a cross-domain question (e.g. "Could operational issues explain sales decline?"), select BOTH relevant specialists (e.g. ["finance", "ops"]).
4. If the user asks a broad strategic question (e.g. "What should I focus on this week?"), select all relevant specialists (["finance", "ops", "marketing"]).
5. If the user changes topic (e.g., "Forget that. What tasks are blocked?"), recognize the context switch and route ONLY to the new domain.
6. If the user asks a follow-up ("Why?", "Explain that", "What should I do?"), use the conversation history to identify the referenced subject.

Respond ONLY with a valid JSON object matching this exact schema:
{
  "clarification_needed": false,
  "clarification_question": "",
  "specialists": ["finance"],
  "resolved_intent": "User is asking about sales trajectory",
  "specialist_queries": {
    "finance": "How are sales performing across our products?",
    "ops": "",
    "marketing": ""
  }
}"""


def _detect_ambiguity_rule(message: str, history: list) -> str | None:
    """Heuristic check for ambiguous queries that lack domain context."""
    cleaned = message.strip().lower().rstrip("?.!")
    if cleaned in ("show me performance", "how is performance", "performance", "check performance", "performance report"):
        # If there's recent history discussing a specific domain, use it; otherwise ask
        if not history:
            return "Do you mean sales performance, operational task performance, or marketing campaign performance?"
    if cleaned in ("how are things", "what's the status", "status update", "give me an update"):
        if not history:
            return "Would you like an update on Finance, Operations, Marketing, or a unified Executive Briefing?"
    return None


def _fallback_route(message: str, history: list) -> list[str]:
    """Reliable heuristic fallback routing if LLM JSON parsing fails."""
    m = message.lower()

    # Topic pivot check
    if "forget that" in m or "never mind" in m or "ignore that" in m:
        # Evaluate remainder of message
        m = re.sub(r"^(forget that|never mind|ignore that)[.,!\s]*", "", m)

    # Specific domain keywords
    has_finance = any(k in m for k in ["revenue", "sales", "financ", "alphaapp", "betasuite", "growth", "forecast", "pricing", "dollar", "money", "$"])
    has_ops = any(k in m for k in ["task", "blocked", "stale", "operat", "priya", "tom", "aws", "ticket", "roadmap", "schedule", "work", "bottleneck"])
    has_mktg = any(k in m for k in ["campaign", "market", "ctr", "conversion", "ad ", "ads", "segment", "region", "demographic", "click"])

    # Cross-domain / Executive focus
    if any(k in m for k in ["focus on this week", "what should i focus", "biggest business risk", "executive summary", "business health", "overall priorities"]):
        return ["finance", "ops", "marketing"]

    # Explicit cross-domain pairings
    if (has_finance and has_ops) or ("sales" in m and "operat" in m):
        return ["finance", "ops"]
    if (has_finance and has_mktg) or ("sales" in m and "campaign" in m):
        return ["finance", "marketing"]

    specs = []
    if has_finance:
        specs.append("finance")
    if has_ops:
        specs.append("ops")
    if has_mktg:
        specs.append("marketing")

    if specs:
        return specs

    # Pronoun / follow-up check: look at last turns
    if any(p in m for p in ["why", "how come", "what about", "explain", "detail", "tell me more"]):
        if history:
            for turn in reversed(history):
                content = turn.get("content", "").lower()
                if any(k in content for k in ["revenue", "sales", "alphaapp", "betasuite"]):
                    return ["finance"]
                if any(k in content for k in ["blocked", "task", "priya", "tom"]):
                    return ["ops"]
                if any(k in content for k in ["campaign", "ctr", "conversion"]):
                    return ["marketing"]

    return ["finance"]  # Default to finance if general business query


def run_executive_turn(message: str, history: list[dict] = None) -> dict:
    """
    Executes a single conversational turn with the Executive Chief of Staff:
    1. Evaluates conversational history and intent.
    2. Detects ambiguity and returns clarification if needed.
    3. Dynamically calls 0, 1, or multiple specialist agents.
    4. Synthesizes findings into a natural, strategic executive answer.
    """
    history = history or []
    specialists_used = []
    steps_taken = 0

    # 1. Quick Ambiguity Check
    clarify_question = _detect_ambiguity_rule(message, history)
    if clarify_question:
        return {
            "response": clarify_question,
            "specialists_used": [],
            "metadata": {
                "steps": 0,
                "intent": "clarification_requested",
                "provider": "direct",
            },
        }

    # 2. Intent & Specialist Routing via LLM
    recent_history = history[-6:] if len(history) > 6 else history
    history_summary = []
    for h in recent_history:
        history_summary.append(f"{h.get('role', 'user').upper()}: {h.get('content', '')[:140]}")

    routing_prompt = [
        {"role": "system", "content": ROUTER_PROMPT},
        {
            "role": "user",
            "content": (
                f"Conversation History:\n"
                f"{chr(10).join(history_summary) if history_summary else 'No prior conversation.'}\n\n"
                f"Current User Message: {message}"
            ),
        },
    ]

    selected_specialists = []
    clarification_msg = None
    specialist_queries = {}

    try:
        raw_routing, provider_used = chat_completion(routing_prompt, max_tokens=150, temperature=0.1, return_meta=True)
        # Parse JSON from response
        clean_json = raw_routing.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()

        parsed = json.loads(clean_json)

        if parsed.get("clarification_needed") and parsed.get("clarification_question"):
            return {
                "response": parsed["clarification_question"],
                "specialists_used": [],
                "metadata": {
                    "steps": 0,
                    "intent": "clarification_requested",
                    "provider": provider_used,
                },
            }

        selected_specialists = parsed.get("specialists", [])
        specialist_queries = parsed.get("specialist_queries", {})
    except Exception as e:
        # Fallback to rule-based router if JSON parse or model routing is inconclusive
        selected_specialists = _fallback_route(message, history)
        provider_used = "groq"

    # Limit to MAX_AGENT_STEPS and clean list
    valid_specs = ["finance", "ops", "marketing"]
    selected_specialists = [s.lower() for s in selected_specialists if s.lower() in valid_specs][:MAX_AGENT_STEPS]

    if not selected_specialists:
        selected_specialists = _fallback_route(message, history)

    # 3. Execute Specialist Tools
    specialist_reports = {}
    for spec in selected_specialists:
        steps_taken += 1
        spec_query = specialist_queries.get(spec) or message

        # Include prior conversation context when querying specialist
        if spec == "finance":
            rep = run_finance_query_structured(spec_query, history=history)
            specialist_reports["finance"] = rep
            specialists_used.append("finance")
        elif spec == "ops":
            rep = run_ops_query_structured(spec_query, history=history)
            specialist_reports["ops"] = rep
            specialists_used.append("ops")
        elif spec == "marketing":
            rep = run_marketing_query_structured(spec_query, history=history)
            specialist_reports["marketing"] = rep
            specialists_used.append("marketing")

    # 4. Synthesize Executive Response
    synthesis_context = ["SPECIALIST FINDINGS:"]
    for s_name, report in specialist_reports.items():
        synthesis_context.append(f"[{s_name.upper()} SPECIALIST REPORT]:\n{report.get('answer', '')}")
        if report.get("warnings"):
            synthesis_context.append(f"[{s_name.upper()} CRITICAL ALERTS]: {'; '.join(report.get('warnings', []))}")

    synth_messages = [
        {"role": "system", "content": CHIEF_OF_STAFF_SYNTHESIS_PROMPT},
    ]

    # Add prior history turns so synthesizer maintains tone and context
    for turn in recent_history:
        r = turn.get("role")
        c = turn.get("content", "")
        if r in ("user", "assistant") and c:
            synth_messages.append({"role": r, "content": c})

    synth_messages.append({
        "role": "user",
        "content": (
            f"User Question: {message}\n\n"
            f"{chr(10).join(synthesis_context)}\n\n"
            "Please deliver a clear, conversational, executive synthesis addressing my question."
        ),
    })

    final_answer, synth_provider = chat_completion(
        synth_messages,
        max_tokens=240,
        temperature=0.3,
        return_meta=True,
    )

    return {
        "response": final_answer,
        "specialists_used": specialists_used,
        "metadata": {
            "steps": steps_taken,
            "provider": synth_provider,
            "intent": "synthesized_executive_response",
        },
    }
