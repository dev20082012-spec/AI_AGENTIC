"""
AGentic Resolve — Comprehensive Agent Quality & Evaluation Suite

Tests:
1. Context Test: Multi-turn reference resolution (Sales -> Why? -> Which product?)
2. Cross-Domain Test: Correlating Operations & Marketing to Sales
3. Topic Switch Test: Pivot from Marketing to Operations
4. Ambiguity Test: Verify clarification request (0 specialists)
5. Repetition Test: Verify targeted answers without baseline sales regurgitation
6. Briefing Reliability Test: Run /api/briefing and verify structured sections & status
7. Streaming Endpoint Test: Verify SSE events on /api/chat/executive/stream
"""

import sys
import os
import time
import json
import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

BASE_URL = "http://127.0.0.1:8000"


def run_evaluation():
    print("=" * 75)
    print("AGENTIC RESOLVE — AGENT QUALITY & RELIABILITY EVALUATION SUITE")
    print("=" * 75)

    passed_count = 0
    total_count = 7

    # ──────────────────────────────────────────────────────────────────────────
    # 1. Context Test
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[EVAL 1] Context Test: Multi-Turn Reference Resolution")
    r1 = requests.post(f"{BASE_URL}/api/chat/executive", json={"message": "How are sales performing?", "history": []}, timeout=90)
    assert r1.status_code == 200, f"Step 1 failed: {r1.text}"
    d1 = r1.json()
    assert "finance" in d1.get("specialists_used", []), "Expected finance specialist"

    hist = [
        {"role": "user", "content": "How are sales performing?"},
        {"role": "assistant", "content": d1["response"]},
    ]
    r2 = requests.post(f"{BASE_URL}/api/chat/executive", json={"message": "Why?", "history": hist}, timeout=90)
    assert r2.status_code == 200, f"Step 2 failed: {r2.text}"
    d2 = r2.json()
    assert "finance" in d2.get("specialists_used", []), "Expected finance follow-up"

    hist.extend([
        {"role": "user", "content": "Why?"},
        {"role": "assistant", "content": d2["response"]},
    ])
    r3 = requests.post(f"{BASE_URL}/api/chat/executive", json={"message": "Which product is responsible?", "history": hist}, timeout=90)
    assert r3.status_code == 200, f"Step 3 failed: {r3.text}"
    d3 = r3.json()
    assert any(p in d3["response"] for p in ["AlphaApp", "BetaSuite"]), "Expected product breakdown in response"
    print("  -> Passed Context Test (3 turns chained).")
    passed_count += 1
    time.sleep(1.0)

    # ──────────────────────────────────────────────────────────────────────────
    # 2. Cross-Domain Test
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[EVAL 2] Cross-Domain Test: Correlating Operations to Sales")
    r_cd = requests.post(
        f"{BASE_URL}/api/chat/executive",
        json={
            "message": "Could operations be contributing to any product bottlenecks?",
            "history": hist,
        },
        timeout=90,
    )
    assert r_cd.status_code == 200, f"Cross-domain failed: {r_cd.text}"
    d_cd = r_cd.json()
    specs = d_cd.get("specialists_used", [])
    assert "ops" in specs, f"Expected ops specialist in cross-domain, got {specs}"
    print(f"  -> Specialists consulted: {specs}")
    print("  -> Passed Cross-Domain Test.")
    passed_count += 1
    time.sleep(1.0)

    # ──────────────────────────────────────────────────────────────────────────
    # 3. Topic Switch Test
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[EVAL 3] Topic Switch Test: Pivot from Marketing to Operations")
    r_ts1 = requests.post(f"{BASE_URL}/api/chat/executive", json={"message": "Tell me about marketing.", "history": []}, timeout=90)
    assert r_ts1.status_code == 200
    d_ts1 = r_ts1.json()

    hist_ts = [
        {"role": "user", "content": "Tell me about marketing."},
        {"role": "assistant", "content": d_ts1["response"]},
    ]
    r_ts2 = requests.post(
        f"{BASE_URL}/api/chat/executive",
        json={"message": "Forget that. Which tasks are blocked?", "history": hist_ts},
        timeout=90,
    )
    assert r_ts2.status_code == 200
    d_ts2 = r_ts2.json()
    assert "ops" in d_ts2.get("specialists_used", []) and "marketing" not in d_ts2.get("specialists_used", []), "Topic pivot must route strictly to ops"
    print(f"  -> Specialists consulted after pivot: {d_ts2.get('specialists_used')}")
    print("  -> Passed Topic Switch Test.")
    passed_count += 1
    time.sleep(1.0)

    # ──────────────────────────────────────────────────────────────────────────
    # 4. Ambiguity Test
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[EVAL 4] Ambiguity Test: Clarification Request")
    r_amb = requests.post(f"{BASE_URL}/api/chat/executive", json={"message": "Show me performance.", "history": []}, timeout=90)
    assert r_amb.status_code == 200
    d_amb = r_amb.json()
    assert len(d_amb.get("specialists_used", [])) == 0, "Expected 0 specialists for ambiguous prompt"
    assert "?" in d_amb.get("response", ""), "Expected clarifying question"
    print(f"  -> Clarification response: {d_amb.get('response')}")
    print("  -> Passed Ambiguity Test.")
    passed_count += 1
    time.sleep(1.0)

    # ──────────────────────────────────────────────────────────────────────────
    # 5. Repetition Test
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[EVAL 5] Repetition Test: Non-Repetitive Synthesis")
    # Turn 1: Sales
    r_rep1 = requests.post(f"{BASE_URL}/api/chat/executive", json={"message": "How are sales performing?", "history": []}, timeout=90)
    d_rep1 = r_rep1.json()
    t1_text = d_rep1["response"]

    # Turn 2: What should I do?
    r_rep2 = requests.post(
        f"{BASE_URL}/api/chat/executive",
        json={
            "message": "What should I do about it?",
            "history": [
                {"role": "user", "content": "How are sales performing?"},
                {"role": "assistant", "content": t1_text},
            ],
        },
        timeout=90,
    )
    d_rep2 = r_rep2.json()
    t2_text = d_rep2["response"]

    # Verify that turn 2 focuses on recommendations and does NOT merely duplicate turn 1 text
    assert t1_text != t2_text, "Turn 2 must not duplicate Turn 1 response"
    assert any(w in t2_text.lower() for w in ["action", "recommend", "priorit", "focus", "step"]), "Expected action-oriented response in Turn 2"
    print("  -> Passed Repetition Test (Turn 2 provides actions rather than reprinting Turn 1 report).")
    passed_count += 1
    time.sleep(1.0)

    # ──────────────────────────────────────────────────────────────────────────
    # 6. Briefing Reliability Test
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[EVAL 6] Briefing Reliability Test: Full Business Briefing")
    r_br = requests.post(
        f"{BASE_URL}/api/briefing",
        json={"query": "Give me this week's executive briefing: revenue trend, pending ops items, and campaign performance."},
        timeout=90,
    )
    assert r_br.status_code == 200, f"Briefing failed: {r_br.text}"
    d_br = r_br.json()
    assert "synthesized_briefing" in d_br, "Expected synthesized_briefing in response"
    assert "specialist_results" in d_br, "Expected specialist_results in response"

    # Verify structured fields
    for s_key in ("finance", "ops", "marketing"):
        s_info = d_br["specialist_results"].get(s_key, {})
        assert s_info.get("status") in ("consulted", "unavailable"), f"Invalid status for {s_key}"

    assert len(d_br.get("top_actions", [])) > 0 or len(d_br.get("key_risks", [])) > 0, "Expected structured actions or risks"
    print(f"  -> Generated at: {d_br.get('generated_at')}")
    print(f"  -> Top actions count: {len(d_br.get('top_actions', []))}")
    print(f"  -> Specialists called: {d_br.get('specialists_called')}")
    print("  -> Passed Briefing Reliability Test.")
    passed_count += 1
    time.sleep(1.0)

    # ──────────────────────────────────────────────────────────────────────────
    # 7. Streaming Endpoint Test
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[EVAL 7] Streaming Endpoint Test: /api/chat/executive/stream")
    r_stream = requests.post(
        f"{BASE_URL}/api/chat/executive/stream",
        json={"message": "Hello", "history": []},
        stream=True,
        timeout=30,
    )
    assert r_stream.status_code == 200, f"Streaming failed: {r_stream.status_code}"
    assert "text/event-stream" in r_stream.headers.get("Content-Type", ""), "Expected text/event-stream content type"

    tokens_received = 0
    events_found = set()
    for line in r_stream.iter_lines():
        if line:
            line_str = line.decode("utf-8", errors="replace")
            if line_str.startswith("data: "):
                try:
                    payload = json.loads(line_str[6:])
                    event_type = payload.get("event")
                    if event_type:
                        events_found.add(event_type)
                    if event_type == "token":
                        tokens_received += 1
                except Exception:
                    pass

    assert "token" in events_found or "done" in events_found, f"Expected SSE events, got: {events_found}"
    print(f"  -> Events received: {events_found}, tokens count: {tokens_received}")
    print("  -> Passed Streaming Endpoint Test.")
    passed_count += 1

    print("\n" + "=" * 75)
    print(f"ALL EVALUATION TESTS ({passed_count}/{total_count}) PASSED WITH 100% ACCURACY!")
    print("=" * 75)


if __name__ == "__main__":
    run_evaluation()
