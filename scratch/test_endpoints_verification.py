import json
import urllib.request
import time

BASE_URL = "http://127.0.0.1:8000"

def get(path):
    req = urllib.request.Request(f"{BASE_URL}{path}")
    with urllib.request.urlopen(req, timeout=15) as res:
        return res.status, json.loads(res.read().decode())

def post(path, data):
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=45) as res:
        return res.status, json.loads(res.read().decode())

def main():
    print("Testing API Health...")
    status, health = get("/api/health")
    assert status == 200, f"Health failed: {status}"
    print(f"Health OK: {health}")

    print("\nTesting Observability Endpoint...")
    status, obs = get("/api/observability")
    assert status == 200, f"Observability failed: {status}"
    print(f"Observability OK: status={obs.get('status')}, summary={obs.get('summary')}")

    print("\nTesting Thread Persistence...")
    status, threads = get("/api/threads")
    assert status == 200, f"Threads list failed: {status}"
    print(f"Initial threads count: {len(threads.get('threads', []))}")

    # Create a test thread
    status, saved = post("/api/threads", {
        "specialist": "executive",
        "title": "Test Executive Session",
        "messages": [
            {"role": "user", "content": "How are sales performing?", "timestamp": "12:00 PM"},
            {"role": "assistant", "content": "AlphaApp revenue grew +5.6% MoM to $125,000.", "timestamp": "12:01 PM"}
        ]
    })
    assert status == 200, f"Thread save failed: {status}"
    t_id = saved.get("thread_id")
    print(f"Created thread: {t_id}")

    status, fetched = get(f"/api/threads/{t_id}")
    assert status == 200 and fetched.get("title") == "Test Executive Session"
    print("Thread retrieval verified!")

    # Verify observability recorded things
    status, obs2 = get("/api/observability")
    print(f"Observability after thread: {obs2.get('summary')}")

    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
