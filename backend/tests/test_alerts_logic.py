from app.observability import metrics
from app.observability import alerts


def test_alerts_trigger_on_high_error_rate(monkeypatch):
    triggered = {}

    def fake_alert(event, value, threshold, tenant_id=None):
        triggered["event"] = event
        triggered["value"] = value

    monkeypatch.setattr(alerts, "_alert", fake_alert)
    # simulate totals
    metrics.inc_counter("api_requests_total", {"path": "/x", "method": "GET", "status_code": "500"}, 2)
    metrics.inc_counter("api_requests_total", {"path": "/x", "method": "GET", "status_code": "200"}, 10)
    alerts.run_alert_check_once()
    assert triggered.get("event") == "error_rate_high"

