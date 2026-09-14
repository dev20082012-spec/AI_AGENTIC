import os
import json
from datetime import datetime, date

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_EMP_JSON = os.path.join(_DATA_DIR, "employee_updates.json")
_STALE_DAYS = 10


def _load_and_analyze() -> str:
    try:
        with open(_EMP_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)

        today = date.today()
        counts = {"done": 0, "in_progress": 0, "pending": 0, "blocked": 0}
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
            if days_old is not None and days_old >= _STALE_DAYS and status != "done":
                reasons.append(f"STALE ({days_old}d)")

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

        return "\n".join(lines)

    except FileNotFoundError:
        return f"ERROR: {_EMP_JSON} not found."
    except Exception as e:
        return f"ERROR computing ops data: {e}"


def run_ops_query(query: str, history: list = None) -> str:
    from groq import Groq
    data_summary = _load_and_analyze()
    client = Groq(api_key=os.environ["GROQ_API_KEY"], max_retries=5)

    messages = [
        {
            "role": "system",
            "content": (
                "Operations manager. Highlight key blockers, stale items, and status from the ops summary in 2-3 short bullets (under 75 words total)."
            ),
        }
    ]

    if history:
        for msg in history:
            role = msg.get("role")
            content = msg.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})

    user_content = f"{query}\n\n[Operations Context]\n{data_summary}"
    messages.append({"role": "user", "content": user_content})

    resp = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=messages,
        max_tokens=200,
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()


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
