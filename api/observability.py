"""
AGentic Resolve — Observability & Execution Telemetry

Provides lightweight, in-memory & persisted execution tracking:
- Request latency, provider and model usage
- Failover counts and error rates
- Specialist invocation distribution
- High-level trace logs (zero secrets, zero chain-of-thought)
"""

import time
from datetime import datetime, timezone
from typing import Any

# Ring buffer for recent execution traces (last 100 requests)
_MAX_TRACES = 100
_execution_traces: list[dict[str, Any]] = []

_stats = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "fallback_invocations": 0,
    "total_latency_ms": 0,
    "specialist_calls": {
        "finance": 0,
        "ops": 0,
        "marketing": 0,
    },
    "providers_used": {
        "groq": 0,
        "openrouter": 0,
        "direct": 0,
    },
}


def record_execution(
    endpoint: str,
    intent: str,
    provider: str,
    model: str,
    latency_ms: int,
    specialists_used: list[str],
    success: bool = True,
    fallback_used: bool = False,
    error: str | None = None,
) -> dict:
    """Records an execution trace and updates aggregate metrics."""
    global _execution_traces, _stats

    _stats["total_requests"] += 1
    if success:
        _stats["successful_requests"] += 1
    else:
        _stats["failed_requests"] += 1

    if fallback_used:
        _stats["fallback_invocations"] += 1

    _stats["total_latency_ms"] += latency_ms

    prov_key = provider.lower() if provider else "unknown"
    _stats["providers_used"][prov_key] = _stats["providers_used"].get(prov_key, 0) + 1

    for spec in specialists_used:
        s_key = spec.lower()
        if s_key in _stats["specialist_calls"]:
            _stats["specialist_calls"][s_key] += 1

    trace = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoint": endpoint,
        "intent": intent,
        "provider": provider,
        "model": model,
        "latency_ms": latency_ms,
        "specialists_used": specialists_used,
        "fallback_used": fallback_used,
        "success": success,
        "error": error,
    }

    _execution_traces.append(trace)
    if len(_execution_traces) > _MAX_TRACES:
        _execution_traces = _execution_traces[-_MAX_TRACES:]

    return trace


def get_observability_summary() -> dict:
    """Returns real-time aggregate health, performance, and trace metrics."""
    total = _stats["total_requests"]
    avg_latency = round(_stats["total_latency_ms"] / total, 1) if total > 0 else 0
    success_rate = round((_stats["successful_requests"] / total) * 100, 1) if total > 0 else 100.0

    return {
        "status": "healthy",
        "uptime_seconds": int(time.time()),
        "summary": {
            "total_requests": total,
            "success_rate_pct": success_rate,
            "avg_latency_ms": avg_latency,
            "fallback_invocations": _stats["fallback_invocations"],
        },
        "specialist_distribution": dict(_stats["specialist_calls"]),
        "provider_distribution": dict(_stats["providers_used"]),
        "recent_traces": list(reversed(_execution_traces[-15:])),
    }
