import requests
import json
import time
import sys

# Force UTF-8 stdout on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("=" * 70)
    print("EXECUTIVE CHIEF OF STAFF CONVERSATIONAL ACCEPTANCE TEST SUITE")
    print("=" * 70)

    # ── TEST 1: Single domain - Finance ─────────────────────────────────────
    print("\n[TEST 1] User: 'How are sales performing?'")
    r1 = requests.post(
        f"{BASE_URL}/api/chat/executive",
        json={"message": "How are sales performing?", "history": []},
        timeout=30
    )
    assert r1.status_code == 200, f"Failed: {r1.status_code} {r1.text}"
    d1 = r1.json()
    print("  -> Status:", r1.status_code)
    print("  -> Specialists used:", d1.get("specialists_used"))
    print("  -> Response snippet:", d1.get("response")[:120].replace('\n', ' '), "...")
    assert "finance" in d1.get("specialists_used", []), "Expected 'finance' to be consulted"
    print("  [PASS] Test 1 passed.", flush=True)
    time.sleep(2)

    # ── TEST 2: Pronoun / Follow-up - 'Why?' with history ────────────────────
    print("\n[TEST 2] User: 'Why?' (Follow-up to sales performance)", flush=True)
    history_t2 = [
        {"role": "user", "content": "How are sales performing?"},
        {"role": "assistant", "content": d1.get("response")},
    ]
    r2 = requests.post(
        f"{BASE_URL}/api/chat/executive",
        json={"message": "Why is that happening?", "history": history_t2},
        timeout=30
    )
    assert r2.status_code == 200, f"Failed: {r2.status_code} {r2.text}"
    d2 = r2.json()
    print("  -> Status:", r2.status_code, flush=True)
    print("  -> Specialists used:", d2.get("specialists_used"), flush=True)
    print("  -> Response snippet:", d2.get("response")[:120].replace('\n', ' '), "...", flush=True)
    assert "finance" in d2.get("specialists_used", []), "Expected 'finance' context retained"
    print("  [PASS] Test 2 passed.", flush=True)

    time.sleep(2)

    # ── TEST 3: Cross-domain - Operations related to sales ──────────────────
    print("\n[TEST 3] User: 'What operational issues might be related?'", flush=True)
    history_t3 = history_t2 + [
        {"role": "user", "content": "Why is that happening?"},
        {"role": "assistant", "content": d2.get("response")},
    ]
    r3 = requests.post(
        f"{BASE_URL}/api/chat/executive",
        json={"message": "What operational issues might be related?", "history": history_t3},
        timeout=30
    )
    assert r3.status_code == 200, f"Failed: {r3.status_code} {r3.text}"
    d3 = r3.json()
    print("  -> Status:", r3.status_code, flush=True)
    print("  -> Specialists used:", d3.get("specialists_used"), flush=True)
    print("  -> Response snippet:", d3.get("response")[:120].replace('\n', ' '), "...", flush=True)
    assert "ops" in d3.get("specialists_used", []), "Expected 'ops' to be consulted"
    print("  [PASS] Test 3 passed.", flush=True)

    time.sleep(2)

    # ── TEST 4: Single domain - Marketing only ───────────────────────────────
    print("\n[TEST 4] User: 'What marketing segment performed best?'", flush=True)
    r4 = requests.post(
        f"{BASE_URL}/api/chat/executive",
        json={"message": "What marketing segment performed best?", "history": []},
        timeout=30
    )
    assert r4.status_code == 200, f"Failed: {r4.status_code} {r4.text}"
    d4 = r4.json()
    print("  -> Status:", r4.status_code, flush=True)
    print("  -> Specialists used:", d4.get("specialists_used"), flush=True)
    print("  -> Response snippet:", d4.get("response")[:120].replace('\n', ' '), "...", flush=True)
    assert "marketing" in d4.get("specialists_used", []) and "ops" not in d4.get("specialists_used", []), "Expected Marketing only"
    print("  [PASS] Test 4 passed.", flush=True)

    time.sleep(2)

    # ── TEST 5: Topic Pivot - 'Forget that. Which tasks are blocked?' ─────────
    print("\n[TEST 5] User: 'Forget that. Which tasks are blocked?'", flush=True)
    history_t5 = [
        {"role": "user", "content": "Tell me about marketing."},
        {"role": "assistant", "content": "Our latest marketing campaign generated 11,398 conversions with 4.45% CTR."},
    ]
    r5 = requests.post(
        f"{BASE_URL}/api/chat/executive",
        json={"message": "Forget that. Which tasks are blocked?", "history": history_t5},
        timeout=30
    )
    assert r5.status_code == 200, f"Failed: {r5.status_code} {r5.text}"
    d5 = r5.json()
    print("  -> Status:", r5.status_code, flush=True)
    print("  -> Specialists used:", d5.get("specialists_used"), flush=True)
    print("  -> Response snippet:", d5.get("response")[:120].replace('\n', ' '), "...", flush=True)
    assert "ops" in d5.get("specialists_used", []) and "marketing" not in d5.get("specialists_used", []), "Expected Ops only after topic pivot"
    print("  [PASS] Test 5 passed.", flush=True)

    time.sleep(2)

    # ── TEST 6: Ambiguity - 'Show me performance.' ───────────────────────────
    print("\n[TEST 6] User: 'Show me performance.' (Ambiguous query)", flush=True)
    r6 = requests.post(
        f"{BASE_URL}/api/chat/executive",
        json={"message": "Show me performance.", "history": []},
        timeout=30
    )
    assert r6.status_code == 200, f"Failed: {r6.status_code} {r6.text}"
    d6 = r6.json()
    print("  -> Status:", r6.status_code, flush=True)
    print("  -> Specialists used:", d6.get("specialists_used"), flush=True)
    print("  -> Response:", d6.get("response"), flush=True)
    assert len(d6.get("specialists_used", [])) == 0, "Expected 0 specialists on ambiguous query"
    assert "?" in d6.get("response", ""), "Expected clarifying question"
    print("  [PASS] Test 6 passed.", flush=True)

    time.sleep(2)

    # ── TEST 7: Cross-domain Executive Focus ─────────────────────────────────
    print("\n[TEST 7] User: 'What should I focus on this week?'", flush=True)
    r7 = requests.post(
        f"{BASE_URL}/api/chat/executive",
        json={"message": "What should I focus on this week?", "history": []},
        timeout=60
    )
    assert r7.status_code == 200, f"Failed: {r7.status_code} {r7.text}"
    d7 = r7.json()
    print("  -> Status:", r7.status_code, flush=True)
    print("  -> Specialists used:", d7.get("specialists_used"), flush=True)
    print("  -> Response snippet:", d7.get("response")[:150].replace('\n', ' '), "...", flush=True)
    assert len(d7.get("specialists_used", [])) >= 2, "Expected multiple specialists consulted for weekly executive focus"
    print("  [PASS] Test 7 passed.", flush=True)

    time.sleep(2)

    # ── TEST 8: Backwards compatibility - /api/briefing ──────────────────────
    print("\n[TEST 8] POST /api/briefing (Existing structured briefing)", flush=True)
    r8 = requests.post(
        f"{BASE_URL}/api/briefing",
        json={"query": "Give me this week's briefing: revenue trend, pending ops items, and last campaign."},
        timeout=60
    )
    assert r8.status_code == 200, f"Failed: {r8.status_code} {r8.text}"
    d8 = r8.json()
    print("  -> Status:", r8.status_code, flush=True)
    print("  -> Specialists called:", d8.get("specialists_called"), flush=True)
    assert "synthesized_briefing" in d8, "Expected synthesized_briefing in briefing response"
    print("  [PASS] Test 8 passed.", flush=True)

    # ── TEST 9: Backwards compatibility - /api/chat/finance ──────────────────
    print("\n[TEST 9] POST /api/chat/finance (Direct specialist chat)", flush=True)
    r9 = requests.post(
        f"{BASE_URL}/api/chat/finance",
        json={"message": "What is the 3-month forecast for AlphaApp?", "history": []},
        timeout=30
    )
    assert r9.status_code == 200, f"Failed: {r9.status_code} {r9.text}"
    d9 = r9.json()
    print("  -> Status:", r9.status_code, flush=True)
    print("  -> Response snippet:", d9.get("response")[:100].replace('\n', ' '), "...", flush=True)
    assert len(d9.get("response", "")) > 10, "Expected valid response from finance specialist"
    print("  [PASS] Test 9 passed.", flush=True)

    print("\n" + "=" * 70)
    print("ALL 9 ACCEPTANCE TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
