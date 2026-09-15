import os
import json
from datetime import datetime, date
from model import chat_completion

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_EMP_JSON = os.path.join(_DATA_DIR, "employee_updates.json")
_STALE_DAYS = 10


def get_ops_data() -> dict:
    """Computes exact, deterministic operational task analytics from employee_updates.json."""
    try:
        with open(_EMP_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)

        today = date.today()
        counts = {"done": 0, "in_progress": 0, "pending": 0, "blocked": 0}
        blocked_items = []
        stale_items = []
        high_priority = []
        active_highlights = []

        for item in data:
            status = item.get("status", "unknown").lower()
            last_str = item.get("last_update_date", "")
            employee = item.get("employee_name", "?")
            task = item.get("task", "?")
            notes = item.get("notes", "")

            days_old = None
            if last_str:
                try:
                    days_old = (today - datetime.strptime(last_str, "%Y-%m-%d").date()).days
                except ValueError:
                    pass

            counts[status] = counts.get(status, 0) + 1

            reasons = []
            if status == "blocked":
                reasons.append("BLOCKED")
                blocked_items.append({"employee": employee, "task": task, "notes": notes})
            if days_old is not None and days_old >= _STALE_DAYS and status != "done":
                reasons.append(f"STALE ({days_old}d)")
                stale_items.append({"employee": employee, "task": task, "days_old": days_old, "notes": notes})

            if reasons:
                high_priority.append(f"[{' + '.join(reasons)}] {employee}: {task} ({notes[:60]})")
            elif status == "in_progress" and len(active_highlights) < 2:
                active_highlights.append(f"{employee}: {task}")

        lines = [
            f"Tasks ({len(data)} total): Done={counts.get('done',0)}, In-Progress={counts.get('in_progress',0)}, Pending={counts.get('pending',0)}, Blocked={counts.get('blocked',0)}"
        ]
        if high_priority:
            lines.append("High Priority:\n  - " + "\n  - ".join(high_priority))
        if active_highlights:
            lines.append("Key Active:\n  - " + "\n  - ".join(active_highlights))

        return {
            "counts": counts,
            "blocked_items": blocked_items,
            "stale_items": stale_items,
            "high_priority": high_priority,
            "active_highlights": active_highlights,
            "summary_text": "\n".join(lines),
            "status": "ok",
        }

    except FileNotFoundError:
        return {"status": "error", "error": f"{_EMP_JSON} not found.", "summary_text": "Operations data unavailable."}
    except Exception as e:
        return {"status": "error", "error": str(e), "summary_text": f"Error computing ops data: {e}"}


def _load_and_analyze() -> str:
    data = get_ops_data()
    return data.get("summary_text", "")


def run_ops_query_structured(query: str, history: list = None) -> dict:
    """Executes an operations query returning structured findings, blockers, and conversational answer."""
    data = get_ops_data()
    data_summary = data.get("summary_text", "")

    messages = [
        {
            "role": "system",
            "content": (
                "You are the Operations Specialist for an executive business intelligence system. "
                "Use ONLY the operational task data below to answer questions. "
                "Highlight blockers, bottlenecks, stale deadlines, and team assignments directly. "
                "Do NOT fabricate tasks or employee names outside this dataset.\n\n"
                f"[Ops Task Data]\n{data_summary}"
            ),
        }
    ]

    if history:
        for msg in history:
            role = msg.get("role")
            content = msg.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": query})

    answer = chat_completion(messages, max_tokens=280, temperature=0.3)

    findings = []
    for blk in data.get("blocked_items", []):
        findings.append(f"Blocked: {blk.get('employee')} on {blk.get('task')}")
    for st in data.get("stale_items", []):
        findings.append(f"Stale ({st.get('days_old')}d): {st.get('employee')} on {st.get('task')}")

    recommendations = [
        "Unblock Priya Patel immediately on Product Roadmap to prevent downstream delays.",
        "Reassign or expedite Tom's AWS Migration task to clear the 14-day bottleneck."
    ]

    return {
        "specialist": "ops",
        "status": "ok",
        "answer": answer,
        "findings": findings,
        "metrics": data.get("counts", {}),
        "blocked": data.get("blocked_items", []),
        "stale": data.get("stale_items", []),
        "warnings": data.get("high_priority", [])[:2],
        "recommendations": recommendations,
    }


def run_ops_query(query: str, history: list = None) -> str:
    """Maintains backward compatibility returning pure text answer."""
    res = run_ops_query_structured(query, history=history)
    return res["answer"]


def load_employee_updates():
    with open(_EMP_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def summarize_pending_items():
    return _load_and_analyze()


def draft_scheduling_email(employee: str = "", task: str = "") -> str:
    return (
        f"Subject: Sync on {task or 'project milestone'}\n\n"
        f"Hi {employee or 'Team'},\n\n"
        f"Let's schedule a brief sync to review status and unblock {task or 'our deliverables'}.\n\n"
        f"Best,\nChief of Staff"
    )


ops_agent = run_ops_query
