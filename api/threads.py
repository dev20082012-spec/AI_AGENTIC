"""
AGentic Resolve — Server-Side Thread Persistence

Manages persistent conversation threads across sessions and specialists.
Backed by local JSON storage in data/threads_store.json.
"""

import os
import json
import uuid
from datetime import datetime, timezone
from typing import Any

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_STORE_FILE = os.path.join(_DATA_DIR, "threads_store.json")

_threads: dict[str, dict[str, Any]] = {}


def _load_store():
    global _threads
    if os.path.exists(_STORE_FILE):
        try:
            with open(_STORE_FILE, "r", encoding="utf-8") as f:
                _threads = json.load(f)
        except Exception:
            _threads = {}


def _save_store():
    try:
        os.makedirs(_DATA_DIR, exist_ok=True)
        with open(_STORE_FILE, "w", encoding="utf-8") as f:
            json.dump(_threads, f, indent=2)
    except Exception as e:
        print(f"  [!] Failed to persist threads_store: {e}")


_load_store()


def list_threads(specialist: str | None = None) -> list[dict]:
    """Returns summarized list of active conversation threads."""
    results = []
    for t_id, t_data in _threads.items():
        if specialist and t_data.get("specialist") != specialist:
            continue
        results.append({
            "thread_id": t_id,
            "title": t_data.get("title", "Untitled Thread"),
            "specialist": t_data.get("specialist", "executive"),
            "message_count": len(t_data.get("messages", [])),
            "created_at": t_data.get("created_at"),
            "updated_at": t_data.get("updated_at"),
            "last_snippet": (
                t_data.get("messages", [])[-1].get("content", "")[:90]
                if t_data.get("messages")
                else ""
            ),
        })
    # Sort by most recently updated
    return sorted(results, key=lambda x: x.get("updated_at", ""), reverse=True)


def get_thread(thread_id: str) -> dict | None:
    return _threads.get(thread_id)


def save_thread(
    thread_id: str | None,
    specialist: str,
    messages: list[dict],
    title: str | None = None,
) -> dict:
    """Creates or updates a thread with messages and automatic title derivation."""
    now = datetime.now(timezone.utc).isoformat()
    t_id = thread_id or f"th_{uuid.uuid4().hex[:10]}"

    existing = _threads.get(t_id, {})

    if not title:
        if existing.get("title"):
            title = existing["title"]
        elif messages and len(messages) > 0:
            first_user = next((m.get("content", "") for m in messages if m.get("role") == "user"), "Executive Session")
            title = first_user[:45] + ("..." if len(first_user) > 45 else "")
        else:
            title = "New Consultation"

    thread_record = {
        "thread_id": t_id,
        "title": title,
        "specialist": specialist,
        "created_at": existing.get("created_at", now),
        "updated_at": now,
        "messages": messages,
    }

    _threads[t_id] = thread_record
    _save_store()
    return thread_record


def delete_thread(thread_id: str) -> bool:
    if thread_id in _threads:
        del _threads[thread_id]
        _save_store()
        return True
    return False
