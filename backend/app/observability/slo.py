from __future__ import annotations

import os
import threading
import time
from typing import Dict

from app.observability.metrics import get_registry
from app.observability.alerts import _alert


SLO_CONFIG = {
    "api_latency_p95": {"threshold": 1.0, "metric": "api_latency_seconds"},
    "chat_roundtrip_p95": {"threshold": 1.2, "metric": "api_latency_seconds"},
    "ia_timeout_rate": {"threshold": 1.0, "metric": "ia_requests_total"},
    "widget_error_rate": {"threshold": 0.5, "metric": "api_requests_total"},
}

_SLO_STATUS: Dict[str, str] = {}


def _p95(values: list[float]) -> float:
    if not values:
        return 0.0
    values_sorted = sorted(values)
    idx = int(0.95 * (len(values_sorted) - 1))
    return values_sorted[idx]


def evaluate_slo():
    registry = get_registry()
    status = {}
    api_lat = []
    ia_lat = []
    for vals in registry.histograms.get("api_latency_seconds", {}).values():
        api_lat.extend(vals)
    for vals in registry.histograms.get("ia_latency_seconds", {}).values():
        ia_lat.extend(vals)
    api_p95 = _p95(api_lat)
    chat_p95 = api_p95
    ia_p95 = _p95(ia_lat)
    # ia timeout rate = outcome error
    ia_total = 0.0
    ia_errors = 0.0
    for key, val in registry.counters.get("ia_requests_total", {}).items():
        labels = dict(key)
        ia_total += val
        if labels.get("outcome") == "error":
            ia_errors += val
    ia_timeout_rate = (ia_errors / ia_total) * 100 if ia_total else 0.0
    # widget error rate proxied by api 4xx/5xx on /chat or widget paths
    widget_errors = 0.0
    widget_total = 0.0
    for key, val in registry.counters.get("api_requests_total", {}).items():
        labels = dict(key)
        if labels.get("path", "").startswith("/v1/chat"):
            widget_total += val
            if str(labels.get("status_code")).startswith("4") or str(
                labels.get("status_code")
            ).startswith("5"):
                widget_errors += val
    widget_err_rate = (widget_errors / widget_total) * 100 if widget_total else 0.0

    status["api_latency_p95"] = (
        "ok" if api_p95 < SLO_CONFIG["api_latency_p95"]["threshold"] else "failing"
    )
    status["chat_roundtrip_p95"] = (
        "ok"
        if chat_p95 < SLO_CONFIG["chat_roundtrip_p95"]["threshold"]
        else "failing"
    )
    status["ia_timeout_rate"] = (
        "ok"
        if ia_timeout_rate < SLO_CONFIG["ia_timeout_rate"]["threshold"]
        else "failing"
    )
    status["widget_error_rate"] = (
        "ok"
        if widget_err_rate < SLO_CONFIG["widget_error_rate"]["threshold"]
        else "failing"
    )

    _SLO_STATUS.update(status)
    if status["api_latency_p95"] == "failing":
        _alert("slo_breach_api_latency", api_p95, SLO_CONFIG["api_latency_p95"]["threshold"])
    if status["ia_timeout_rate"] == "failing":
        _alert("slo_breach_ia_timeout", ia_timeout_rate, SLO_CONFIG["ia_timeout_rate"]["threshold"])
    return status


def start_slo_loop():
    if os.getenv("PYTEST_CURRENT_TEST"):
        return
    def _loop():
        while True:
            time.sleep(60)
            try:
                evaluate_slo()
            except Exception:
                pass
    t = threading.Thread(target=_loop, daemon=True)
    t.start()


def get_slo_status():
    if not _SLO_STATUS:
        return evaluate_slo()
    return _SLO_STATUS
