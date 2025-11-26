from fastapi.testclient import TestClient

from app.main import get_application
from app.observability.metrics import get_registry


def test_metrics_middleware_increments(monkeypatch):
    monkeypatch.setenv("DISABLE_DB", "1")
    monkeypatch.setenv("REDIS_URL", "memory://")
    app = get_application()
    client = TestClient(app)
    res = client.get("/v1/health")
    assert res.status_code in (200, 404)  # health may vary
    registry = get_registry()
    count = 0
    for key, val in registry.counters.get("api_requests_total", {}).items():
        labels = dict(key)
        if labels.get("path") == "/v1/health":
            count += val
    assert count >= 1

