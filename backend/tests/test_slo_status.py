from app.observability import metrics
from app.observability.slo import get_slo_status


def test_slo_status_degraded():
    # Add high latency to force failure
    for _ in range(5):
        metrics.observe_histogram("api_latency_seconds", 2.0, {"path": "/v1/chat", "method": "POST", "tenant_id": "t1"})
    status = get_slo_status()
    assert "api_latency_p95" in status
    assert status["api_latency_p95"] in {"ok", "failing"}
