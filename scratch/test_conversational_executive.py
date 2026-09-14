import requests
import json
import time
import sys

# Force UTF-8 stdout on Windows console with line buffering
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

import functools
print = functools.partial(print, flush=True)

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("=" * 75)
    print("EXECUTIVE CHIEF OF STAFF CONVERSATIONAL ACCEPTANCE TEST SUITE")
    print("=" * 75)

    # ══════════════════════════════════════════════════════════════════════════
    # TEST A: Sales -> Why -> Product -> Ops Correlation -> Action
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "─" * 70)
    print("TEST A: Multi-Turn Analytical Thread (Finance -> Ops -> Strategic Actions)")
    print("─" * 70)

    # Turn A1: How are sales performing?
    print("\n[TEST A1] User: 'How are sales performing?'")
    r_a1 = requests.post(
        f"{BASE_URL}/api/chat/executive",
        json={"message": "How are sales performing?", "history": []},
        timeout=60
    )
    assert r_a1.status_code == 200, f"Failed: {r_a1.status_code} {r_a1.text}"
    d_a1 = r_a1.json()
    print("  -> Status:", r_a1.status_code)
    print("  -> Specialists used:", d_a1.get("specialists_used"))
    print("  -> Response snippet:", d_a1.get("response", "")[:120].replace('\n', ' '), "...")
    assert "finance" in d_a1.get("specialists_used", []), "Expected 'finance' to be consulted"
    print("  [PASS] Turn A1 passed.")
    time.sleep(1.5)

    # Turn A2: Why? (Follow-up using previous context)
    print("\n[TEST A2] User: 'Why?' (Follow-up to sales performance)")
    hist_a2 = [
        {"role": "user", "content": "How are sales performing?"},
        {"role": "assistant", "content": d_a1.get("response")},
    ]
    r_a2 = requests.post(
        f"{BASE_URL}/api/chat/executive",
        json={"message": "Why?", "history": hist_a2},
        timeout=60
    )
    assert r_a2.status_code == 200, f"Failed: {r_a2.status_code} {r_a2.text}"
    d_a2 = r_a2.json()
    print("  -> Status:", r_a2.status_code)
    print("  -> Specialists used:", d_a2.get("specialists_used"))
    print("  -> Response snippet:", d_a2.get("response", "")[:120].replace('\n', ' '), "...")
    assert "finance" in d_a2.get("specialists_used", []), "Expected 'finance' context retained"
    print("  [PASS] Turn A2 passed.")
    time.sleep(1.5)

    # Turn A3: Which product is responsible?
    print("\n[TEST A3] User: 'Which product is responsible?'")
    hist_a3 = hist_a2 + [
        {"role": "user", "content": "Why?"},
        {"role": "assistant", "content": d_a2.get("response")},
    ]
    r_a3 = requests.post(
        f"{BASE_URL}/api/chat/executive",
        json={"message": "Which product is responsible?", "history": hist_a3},
        timeout=60
    )
    assert r_a3.status_code == 200, f"Failed: {r_a3.status_code} {r_a3.text}"
    d_a3 = r_a3.json()
    print("  -> Status:", r_a3.status_code)
    print("  -> Specialists used:", d_a3.get("specialists_used"))
    print("  -> Response snippet:", d_a3.get("response", "")[:120].replace('\n', ' '), "...")
    assert "finance" in d_a3.get("specialists_used", []), "Expected 'finance' product breakdown"
    print("  [PASS] Turn A3 passed.")
    time.sleep(1.5)

    # Turn A4: Could operations be contributing?
    print("\n[TEST A4] User: 'Could operations be contributing?'")
    hist_a4 = hist_a3 + [
        {"role": "user", "content": "Which product is responsible?"},
        {"role": "assistant", "content": d_a3.get("response")},
    ]
    r_a4 = requests.post(
        f"{BASE_URL}/api/chat/executive",
        json={"message": "Could operations be contributing?", "history": hist_a4},
        timeout=60
    )
    assert r_a4.status_code == 200, f"Failed: {r_a4.status_code} {r_a4.text}"
    d_a4 = r_a4.json()
    print("  -> Status:", r_a4.status_code)
    print("  -> Specialists used:", d_a4.get("specialists_used"))
    print("  -> Response snippet:", d_a4.get("response", "")[:120].replace('\n', ' '), "...")
    assert "ops" in d_a4.get("specialists_used", []), "Expected 'ops' to be consulted"
    print("  [PASS] Turn A4 passed.")
    time.sleep(1.5)

    # Turn A5: What should I do about it?
    print("\n[TEST A5] User: 'What should I do about it?'")
    hist_a5 = hist_a4 + [
        {"role": "user", "content": "Could operations be contributing?"},
        {"role": "assistant", "content": d_a4.get("response")},
    ]
    r_a5 = requests.post(
        f"{BASE_URL}/api/chat/executive",
        json={"message": "What should I do about it?", "history": hist_a5},
        timeout=60
    )
    assert r_a5.status_code == 200, f"Failed: {r_a5.status_code} {r_a5.text}"
    d_a5 = r_a5.json()
    print("  -> Status:", r_a5.status_code)
    print("  -> Specialists used:", d_a5.get("specialists_used"))
    print("  -> Response snippet:", d_a5.get("response", "")[:150].replace('\n', ' '), "...")
    assert len(d_a5.get("response", "")) > 40, "Expected action-oriented synthesis"
    print("  [PASS] Turn A5 passed.")
    time.sleep(1.5)

    # ══════════════════════════════════════════════════════════════════════════
    # TEST B: Marketing -> Topic Pivot (Forget that. Which tasks are blocked?)
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "─" * 70)
    print("TEST B: Marketing Query & Topic Pivot Handling")
    print("─" * 70)

    # Turn B1: Tell me about marketing.
    print("\n[TEST B1] User: 'Tell me about marketing.'")
    r_b1 = requests.post(
        f"{BASE_URL}/api/chat/executive",
        json={"message": "Tell me about marketing.", "history": []},
        timeout=60
    )
    assert r_b1.status_code == 200, f"Failed: {r_b1.status_code} {r_b1.text}"
    d_b1 = r_b1.json()
    print("  -> Status:", r_b1.status_code)
    print("  -> Specialists used:", d_b1.get("specialists_used"))
    assert "marketing" in d_b1.get("specialists_used", []), "Expected 'marketing' to be consulted"
    print("  [PASS] Turn B1 passed.")
    time.sleep(1.5)

    # Turn B2: Forget that. Which tasks are blocked?
    print("\n[TEST B2] User: 'Forget that. Which tasks are blocked?' (Topic Pivot)")
    hist_b2 = [
        {"role": "user", "content": "Tell me about marketing."},
        {"role": "assistant", "content": d_b1.get("response")},
    ]
    r_b2 = requests.post(
        f"{BASE_URL}/api/chat/executive",
        json={"message": "Forget that. Which tasks are blocked?", "history": hist_b2},
        timeout=60
    )
    assert r_b2.status_code == 200, f"Failed: {r_b2.status_code} {r_b2.text}"
    d_b2 = r_b2.json()
    print("  -> Status:", r_b2.status_code)
    print("  -> Specialists used:", d_b2.get("specialists_used"))
    print("  -> Response snippet:", d_b2.get("response", "")[:120].replace('\n', ' '), "...")
    assert "ops" in d_b2.get("specialists_used", []) and "marketing" not in d_b2.get("specialists_used", []), "Expected 'ops' only after topic pivot"
    print("  [PASS] Turn B2 passed.")
    time.sleep(1.5)

    # ══════════════════════════════════════════════════════════════════════════
    # TEST C: Ambiguity Detection (Show me performance.)
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "─" * 70)
    print("TEST C: Ambiguity Detection & Clarification Request")
    print("─" * 70)

    print("\n[TEST C1] User: 'Show me performance.' (Ambiguous domain query)")
    r_c1 = requests.post(
        f"{BASE_URL}/api/chat/executive",
        json={"message": "Show me performance.", "history": []},
        timeout=60
    )
    assert r_c1.status_code == 200, f"Failed: {r_c1.status_code} {r_c1.text}"
    d_c1 = r_c1.json()
    print("  -> Status:", r_c1.status_code)
    print("  -> Specialists used:", d_c1.get("specialists_used"))
    print("  -> Response:", d_c1.get("response"))
    assert len(d_c1.get("specialists_used", [])) == 0, "Expected 0 specialists on ambiguous query"
    assert "?" in d_c1.get("response", ""), "Expected clarifying question"
    print("  [PASS] Test C passed.")
    time.sleep(1.5)

    # ══════════════════════════════════════════════════════════════════════════
    # TEST D: Cross-Domain Executive Synthesis (What should I focus on this week?)
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "─" * 70)
    print("TEST D: Multi-Domain Strategic Synthesis")
    print("─" * 70)

    print("\n[TEST D1] User: 'What should I focus on this week?'")
    r_d1 = requests.post(
        f"{BASE_URL}/api/chat/executive",
        json={"message": "What should I focus on this week?", "history": []},
        timeout=45
    )
    assert r_d1.status_code == 200, f"Failed: {r_d1.status_code} {r_d1.text}"
    d_d1 = r_d1.json()
    print("  -> Status:", r_d1.status_code)
    print("  -> Specialists used:", d_d1.get("specialists_used"))
    print("  -> Response snippet:", d_d1.get("response", "")[:150].replace('\n', ' '), "...")
    assert len(d_d1.get("specialists_used", [])) >= 2, "Expected multi-specialist consultation"
    print("  [PASS] Test D passed.")
    time.sleep(1.5)

    # ══════════════════════════════════════════════════════════════════════════
    # TEST E: Conversational Greeting (Hello -> 0 specialists, direct answer)
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "─" * 70)
    print("TEST E: General Conversational Greeting (No default to finance)")
    print("─" * 70)

    print("\n[TEST E1] User: 'Hello'")
    r_e1 = requests.post(
        f"{BASE_URL}/api/chat/executive",
        json={"message": "Hello", "history": []},
        timeout=25
    )
    assert r_e1.status_code == 200, f"Failed: {r_e1.status_code} {r_e1.text}"
    d_e1 = r_e1.json()
    print("  -> Status:", r_e1.status_code)
    print("  -> Specialists used:", d_e1.get("specialists_used"))
    print("  -> Response snippet:", d_e1.get("response", "")[:120].replace('\n', ' '), "...")
    assert len(d_e1.get("specialists_used", [])) == 0, "Expected 0 specialists on greeting, NOT finance"
    assert "AlphaApp" not in d_e1.get("response", ""), "Greeting should not include financial report numbers"
    print("  [PASS] Test E passed.")
    time.sleep(1.5)

    # ══════════════════════════════════════════════════════════════════════════
    # TEST F: Backwards Compatibility (/api/briefing & /api/chat/finance)
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "─" * 70)
    print("TEST F: Backwards Compatibility (Fixed Briefing & Direct Specialist)")
    print("─" * 70)

    # F1: POST /api/briefing
    print("\n[TEST F1] POST /api/briefing (Fixed Executive Briefing)")
    r_f1 = requests.post(
        f"{BASE_URL}/api/briefing",
        json={"query": "Give me this week's briefing: revenue trend, pending ops items, and last campaign."},
        timeout=60
    )
    assert r_f1.status_code == 200, f"Failed: {r_f1.status_code} {r_f1.text}"
    d_f1 = r_f1.json()
    print("  -> Status:", r_f1.status_code)
    print("  -> Specialists called:", d_f1.get("specialists_called"))
    assert "synthesized_briefing" in d_f1, "Expected synthesized_briefing in briefing response"
    print("  [PASS] Test F1 passed.")
    time.sleep(1.5)

    # F2: POST /api/chat/finance
    print("\n[TEST F2] POST /api/chat/finance (Direct Finance Specialist Chat)")
    r_f2 = requests.post(
        f"{BASE_URL}/api/chat/finance",
        json={"message": "What is the 3-month forecast for AlphaApp?", "history": []},
        timeout=30
    )
    assert r_f2.status_code == 200, f"Failed: {r_f2.status_code} {r_f2.text}"
    d_f2 = r_f2.json()
    print("  -> Status:", r_f2.status_code)
    print("  -> Response snippet:", d_f2.get("response", "")[:100].replace('\n', ' '), "...")
    assert len(d_f2.get("response", "")) > 10, "Expected valid response from finance specialist"
    print("  [PASS] Test F2 passed.")

    print("\n" + "=" * 75)
    print("ALL TESTS (A, B, C, D, E, F) COMPLETED SUCCESSFULLY WITH 100% ACCURACY!")
    print("=" * 75)

if __name__ == "__main__":
    run_tests()
