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
    "You communicate clearly, strategically, concisely, and authoritatively with senior leaders. "
    "CRITICAL CONVERSATIONAL RULES:\n"
    "1. Answer ONLY the user's specific current request. Address the exact question asked.\n"
    "2. NEVER regurgitate or repeat the full baseline status/sales report on every turn.\n"
    "3. For follow-ups such as 'Why?', 'Which product is responsible?', 'What should I do?':\n"
    "   - Provide targeted analytical reasons, product breakdowns, or decisive action items.\n"
    "   - Do NOT repeat the raw metrics already stated in prior turns.\n"
    "4. Highlight actionable next steps and strategic business implications.\n"
    "5. Use ONLY numbers provided in the specialist findings; never hallucinate or invent business metrics.\n"
    "6. Keep formatting clean, scannable, and professional (short bullets or brief paragraphs)."
)

ROUTER_PROMPT = """You are the Dispatcher & Intent Analyzer for an Executive Chief of Staff AI.
You receive the user's current message and prior conversation history.

Your job is to analyze intent, resolve conversational references, and decide specialist routing:
1. GREETING / GENERAL CHATTER:
   If the message is a general greeting or non-domain query (e.g. "Hello", "Hi", "Who are you?", "What can you do?"):
   Set "is_direct_answer": true, "specialists": [], "resolved_intent": "greeting_or_general".

2. AMBIGUOUS BUSINESS REQUEST:
   If the request asks for a business update or performance but is completely AMBIGUOUS ACROSS DOMAINS (e.g. "Show me performance" or "Give me an update" with NO domain specified):
   Set "clarification_needed": true, "clarification_question": "Do you mean sales performance, operational task performance, or marketing campaign performance?", "specialists": [].
   (Do NOT clarify if domain is clear or if prior conversation establishes context).

3. DOMAIN SPECIALISTS (choose ONLY what is strictly required):
   - "finance": revenue, sales, financial forecasts, AlphaApp, BetaSuite, anomalies, pricing.
   - "ops": tasks, blockers, stale work, team bottlenecks, scheduling, roadmap, Priya, Tom, AWS.
   - "marketing": campaigns, CTR, conversions, ad spend, demographics, regions.

4. CONVERSATIONAL FOLLOW-UPS & REFERENCES:
   - "Why?" after sales -> route to "finance" with query: "Explain why sales performed that way based on the data."
   - "Which product is responsible?" after sales -> route to "finance" with query: "Which product drove the performance and what is the breakdown?"
   - "Could operations be contributing?" after sales -> route to BOTH ["finance", "ops"] with purposeful queries connecting ops blockers to business results.
   - "What should I do about it?" -> route to the relevant domain(s) or synthesize action items based on prior findings.
   - "Tell me about marketing." -> route to "marketing".
   - "Forget that. Which tasks are blocked?" -> TOPIC PIVOT detected: discard prior topics, route ONLY to "ops".
   - "What should I focus on this week?" -> route to ["finance", "ops", "marketing"].

Respond ONLY with a valid JSON object matching this schema:
{
  "is_direct_answer": false,
  "clarification_needed": false,
  "clarification_question": "",
  "specialists": ["finance"],
  "resolved_intent": "User is asking for sales drivers",
  "specialist_queries": {
    "finance": "Targeted question for finance",
    "ops": "Targeted question for ops",
    "marketing": "Targeted question for marketing"
  }
}"""


def _detect_greeting_or_ambiguity(message: str, history: list) -> dict | None:
    """Fast deterministic check for greetings and underspecified ambiguous queries."""
    cleaned = message.strip().lower().rstrip("?.!")
    
    # Greetings & General Chatter
    if cleaned in ("hello", "hi", "hey", "greetings", "good morning", "good afternoon", "who are you", "what can you do"):
        return {
            "type": "direct_answer",
            "response": (
                "Hello! I'm your Executive Chief of Staff. I coordinate intelligence across "
                "Finance (revenue & product trajectories), Operations (team bottlenecks & blocked tasks), "
                "and Marketing (campaign performance & attribution).\n\n"
                "What would you like to review or unblock today?"
            ),
            "intent": "greeting_or_general",
        }

    # Ambiguity check (only when no prior context resolves it)
    if cleaned in ("show me performance", "how is performance", "performance", "check performance", "performance report"):
        if not history:
            return {
                "type": "clarification",
                "response": "Do you mean sales performance, operational task performance, or marketing campaign performance?",
                "intent": "clarification_requested",
            }
    if cleaned in ("how are things", "what's the status", "status update", "give me an update"):
        if not history:
            return {
                "type": "clarification",
                "response": "Would you like an update on Finance, Operations, Marketing, or a unified Executive Briefing?",
                "intent": "clarification_requested",
            }
    return None


def _fallback_route(message: str, history: list) -> tuple[list[str], dict]:
    """Reliable heuristic fallback routing if LLM JSON parsing fails."""
    m = message.lower()
    queries = {}

    # Topic pivot check: e.g. "Forget that. Which tasks are blocked?"
    if any(p in m for p in ["forget that", "never mind", "ignore that", "switch gears"]):
        m_stripped = re.sub(r"^(forget that|never mind|ignore that|switch gears)[.,!\s]*", "", m)
        if any(k in m_stripped for k in ["task", "blocked", "stale", "operat", "priya", "tom"]):
            queries["ops"] = "Which tasks are currently blocked or stale?"
            return ["ops"], queries
        if any(k in m_stripped for k in ["market", "campaign", "ctr"]):
            queries["marketing"] = "How did the latest marketing campaign perform?"
            return ["marketing"], queries
        if any(k in m_stripped for k in ["sales", "revenue"]):
            queries["finance"] = "How are sales performing?"
            return ["finance"], queries

    # Cross-domain / Executive focus
    if any(k in m for k in ["focus on this week", "what should i focus", "biggest business risk", "executive summary", "business health", "overall priorities"]):
        return ["finance", "ops", "marketing"], {
            "finance": "What are our revenue trajectories and product risks?",
            "ops": "Which high-priority tasks or team members are currently blocked?",
            "marketing": "Which campaign segments or demographics should we capitalize on?",
        }

    # Specific domain keywords
    has_finance = any(k in m for k in ["revenue", "sales", "financ", "alphaapp", "betasuite", "growth", "forecast", "pricing", "dollar", "money", "$"])
    has_ops = any(k in m for k in ["task", "blocked", "stale", "operat", "priya", "tom", "aws", "ticket", "roadmap", "schedule", "bottleneck"])
    has_mktg = any(k in m for k in ["campaign", "market", "ctr", "conversion", "ad ", "ads", "segment", "region", "demographic", "click"])

    # Explicit cross-domain pairings (e.g. "Could operations be causing this?")
    if (has_finance and has_ops) or ("sales" in m and "operat" in m) or ("could operation" in m):
        return ["finance", "ops"], {
            "finance": "Contextual sales performance and product targets.",
            "ops": "Check whether operational bottlenecks or stalled tasks plausibly impact sales deliverables.",
        }
    if (has_finance and has_mktg) or ("sales" in m and "campaign" in m):
        return ["finance", "marketing"], {
            "finance": "Sales trajectory.",
            "marketing": "Campaign conversion correlation.",
        }

    specs = []
    if has_finance:
        specs.append("finance")
        queries["finance"] = message
    if has_ops:
        specs.append("ops")
        queries["ops"] = message
    if has_mktg:
        specs.append("marketing")
        queries["marketing"] = message

    if specs:
        return specs, queries

    # Follow-ups (Why?, Which product is responsible?, What should I do?)
    if any(p in m for p in ["why", "how come", "which product", "what should i do", "what about that", "explain", "detail"]):
        if history:
            for turn in reversed(history):
                c = turn.get("content", "").lower()
                if any(k in c for k in ["revenue", "sales", "alphaapp", "betasuite"]):
                    if "product" in m:
                        queries["finance"] = "Which specific product is responsible for the revenue movement and what are the details?"
                    elif "do" in m or "action" in m:
                        queries["finance"] = "What specific financial actions and resource decisions should be taken?"
                    else:
                        queries["finance"] = "Explain the drivers and underlying factors behind the sales trends discussed."
                    return ["finance"], queries
                if any(k in c for k in ["blocked", "task", "priya", "tom"]):
                    queries["ops"] = message
                    return ["ops"], queries
                if any(k in c for k in ["campaign", "ctr", "conversion"]):
                    queries["marketing"] = message
                    return ["marketing"], queries

    # DO NOT default to finance. Return empty if query is unmapped or general.
    return [], {}


def run_executive_turn(message: str, history: list[dict] = None) -> dict:
    """
    Executes a bounded conversational turn with the Executive Chief of Staff:
    1. Evaluates conversational history and intent.
    2. Detects ambiguity and returns clarification if needed.
    3. Handles general conversation/greetings directly.
    4. Dynamically dispatches purposeful queries to domain specialists.
    5. Synthesizes findings into an actionable executive answer without report repetition.
    """
    history = history or []
    specialists_used = []
    steps_taken = 0

    # 1. Fast deterministic check for Greetings & Ambiguity
    fast_check = _detect_greeting_or_ambiguity(message, history)
    if fast_check:
        if fast_check["type"] == "direct_answer":
            return {
                "response": fast_check["response"],
                "specialists_used": [],
                "metadata": {
                    "steps": 0,
                    "intent": fast_check["intent"],
                    "provider": "direct",
                    "model": "rule-based",
                },
            }
        elif fast_check["type"] == "clarification":
            return {
                "response": fast_check["response"],
                "specialists_used": [],
                "metadata": {
                    "steps": 0,
                    "intent": fast_check["intent"],
                    "provider": "direct",
                    "model": "rule-based",
                },
            }

    # 2. Intent & Specialist Routing via LLM
    recent_history = history[-6:] if len(history) > 6 else history
    history_summary = []
    for h in recent_history:
        role = h.get("role", "user").upper()
        content = h.get("content", "").replace("\n", " ")[:140]
        history_summary.append(f"{role}: {content}")

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
    specialist_queries = {}
    resolved_intent = "executive_query"
    provider_meta = {"provider": "groq", "model": "qwen/qwen3.8-27b"}

    try:
        raw_routing, provider_meta = chat_completion(routing_prompt, max_tokens=180, temperature=0.1, return_meta=True)
        clean_json = raw_routing.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()

        parsed = json.loads(clean_json)

        # Handle direct greeting/conversational branch from LLM router
        if parsed.get("is_direct_answer"):
            direct_messages = [
                {
                    "role": "system",
                    "content": (
                        "You are the Executive Chief of Staff for a growing software company. "
                        "Respond warmly, conversationally, and concisely. Mention that you coordinate "
                        "Finance, Operations, and Marketing intelligence to keep executive leadership aligned."
                    ),
                }
            ]
            for turn in recent_history:
                r = turn.get("role")
                c = turn.get("content", "")
                if r in ("user", "assistant") and c:
                    direct_messages.append({"role": r, "content": c})
            direct_messages.append({"role": "user", "content": message})

            direct_ans, direct_meta = chat_completion(direct_messages, max_tokens=160, temperature=0.3, return_meta=True)
            return {
                "response": direct_ans,
                "specialists_used": [],
                "metadata": {
                    "steps": 0,
                    "intent": parsed.get("resolved_intent", "greeting_or_general"),
                    "provider": direct_meta.get("provider", "groq"),
                    "model": direct_meta.get("model", ""),
                },
            }

        # Handle clarification branch
        if parsed.get("clarification_needed") and parsed.get("clarification_question"):
            return {
                "response": parsed["clarification_question"],
                "specialists_used": [],
                "metadata": {
                    "steps": 0,
                    "intent": "clarification_requested",
                    "provider": provider_meta.get("provider", "groq"),
                    "model": provider_meta.get("model", ""),
                },
            }

        selected_specialists = parsed.get("specialists", [])
        specialist_queries = parsed.get("specialist_queries", {})
        resolved_intent = parsed.get("resolved_intent", "executive_query")

    except Exception as e:
        # Fallback to deterministic router
        selected_specialists, specialist_queries = _fallback_route(message, history)

    # Validate and cap specialist steps
    valid_specs = ["finance", "ops", "marketing"]
    selected_specialists = [s.lower() for s in selected_specialists if s.lower() in valid_specs][:MAX_AGENT_STEPS]

    if not selected_specialists:
        # Check if fallback route has an answer or if it's general/unrecognized
        fallback_specs, fallback_q = _fallback_route(message, history)
        if fallback_specs:
            selected_specialists = fallback_specs
            specialist_queries.update(fallback_q)
        else:
            # General query without specific specialist need: answer directly
            direct_messages = [
                {
                    "role": "system",
                    "content": (
                        "You are the Executive Chief of Staff for a growing software company. "
                        "Answer the user conversationally and professionally. If their question is out of domain "
                        "or general, assist them or clarify how Finance, Operations, or Marketing can help."
                    ),
                }
            ]
            for turn in recent_history:
                r = turn.get("role")
                c = turn.get("content", "")
                if r in ("user", "assistant") and c:
                    direct_messages.append({"role": r, "content": c})
            direct_messages.append({"role": "user", "content": message})

            ans, meta = chat_completion(direct_messages, max_tokens=180, temperature=0.3, return_meta=True)
            return {
                "response": ans,
                "specialists_used": [],
                "metadata": {
                    "steps": 0,
                    "intent": "general_direct_response",
                    "provider": meta.get("provider", "groq"),
                    "model": meta.get("model", ""),
                },
            }

    # 3. Purposeful Specialist Invocations
    specialist_reports = {}
    for spec in selected_specialists:
        steps_taken += 1
        spec_query = specialist_queries.get(spec) or message

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
    synthesis_context = []
    for s_name, report in specialist_reports.items():
        synthesis_context.append(f"=== {s_name.upper()} SPECIALIST FINDINGS ===")
        synthesis_context.append(f"Direct Analysis: {report.get('answer', '')}")
        if report.get("findings"):
            synthesis_context.append(f"Key Points: {'; '.join(report.get('findings', []))}")
        if report.get("warnings"):
            synthesis_context.append(f"Critical Alerts: {'; '.join(report.get('warnings', []))}")
        if report.get("recommendations"):
            synthesis_context.append(f"Recommendations: {'; '.join(report.get('recommendations', []))}")

    synth_messages = [
        {"role": "system", "content": CHIEF_OF_STAFF_SYNTHESIS_PROMPT},
    ]

    for turn in recent_history:
        r = turn.get("role")
        c = turn.get("content", "")
        if r in ("user", "assistant") and c:
            synth_messages.append({"role": r, "content": c})

    synth_messages.append({
        "role": "user",
        "content": (
            f"User's Question: {message}\n\n"
            f"{chr(10).join(synthesis_context)}\n\n"
            "Deliver an executive response answering my specific question directly based on the findings above. "
            "Do NOT repeat the entire baseline report."
        ),
    })

    final_answer, synth_meta = chat_completion(
        synth_messages,
        max_tokens=260,
        temperature=0.3,
        return_meta=True,
    )

    return {
        "response": final_answer,
        "specialists_used": specialists_used,
        "metadata": {
            "intent": resolved_intent,
            "steps": steps_taken,
            "provider": synth_meta.get("provider", "groq"),
            "model": synth_meta.get("model", ""),
        },
    }
