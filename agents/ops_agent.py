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
        all_items = []

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
            all_items.append(f"  [{status.upper()}] {employee}: {task}")

            reasons = []
            if status == "blocked":
                reasons.append("BLOCKED")
            if days_old is not None and days_old >= _STALE_DAYS and status != "done":
                reasons.append(f"STALE ({days_old}d)")

            if reasons:
                high_priority.append(
                    f"  !! {employee} | {' + '.join(reasons)} | {task} | {notes[:80]}"
                )

        lines = [f"=== OPS SUMMARY === Total: {len(data)} tasks"]
        lines.append(
            f"  Done: {counts.get('done',0)} | In Progress: {counts.get('in_progress',0)} "
            f"| Pending: {counts.get('pending',0)} | Blocked: {counts.get('blocked',0)}"
        )

        if high_priority:
            lines.append(f"\nHIGH PRIORITY ({len(high_priority)} items):")
            lines.extend(high_priority)

        lines.append("\nALL TASKS:")
        lines.extend(all_items)

        return "\n".join(lines)

    except FileNotFoundError:
        return f"ERROR: {_EMP_JSON} not found."
    except Exception as e:
        return f"ERROR computing ops data: {e}"


def run_ops_query(query: str) -> str:
    from groq import Groq
    data_summary = _load_and_analyze()
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    resp = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a chief-of-staff assistant. Answer the query using the ops data. "
                    "Lead with HIGH PRIORITY items. Max 4 bullet points. Be brief."
                ),
            },
            {
                "role": "user",
                "content": f"Query: {query}\n\n{data_summary}",
            },
        ],
        max_tokens=400,
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()
