from __future__ import annotations

import os
import threading
import time
from typing import Dict

from loguru import logger

from app.observability.metrics import get_registry


ALERT_INTERVAL_SECONDS = 60


def _alert(event: str, value: float, threshold: float, tenant_id: str | None = None):
    payload = {
        "event": "alert",
        "alert_type": event,
        "value": value,
        "threshold": threshold,
        "tenant_id": tenant_id,
    }
    logger.warning(payload)
    # Stub for future Slack/email integration


def _compute_rate(delta_errors: float, delta_total: float) -> float:
    if delta_total <= 0:
        return 0.0
    return (delta_errors / delta_total) * 100.0


def _check_once(prev_counters: Dict[str, float]):
    registry = get_registry()
    # error_rate_high: 5xx >1% en últimos 60s (aprox)
    total = 0.0
    total_all = 0.0
    for key, val in registry.counters.get("api_requests_total", {}).items():
        labels = dict(key)
        if labels.get("status_code"):
            total_all += val
        if str(labels.get("status_code", "")).startswith("5"):
            total += val
    prev_err = prev_counters.get("api_err", 0.0)
    prev_total = prev_counters.get("api_total", 0.0)
    delta_err = total - prev_err
    delta_total = total_all - prev_total
    rate = _compute_rate(delta_err, delta_total)
    if rate > 1.0:
        _alert("error_rate_high", rate, 1.0)
    prev_counters["api_err"] = total
    prev_counters["api_total"] = total_all

    # ia_fallback_rate_high: fallback >10%
    ia_fallback = 0.0
    ia_total = 0.0
    for key, val in registry.counters.get("ia_requests_total", {}).items():
        labels = dict(key)
        ia_total += val
        if labels.get("outcome") == "fallback":
            ia_fallback += val
    prev_ia_fallback = prev_counters.get("ia_fallback", 0.0)
    prev_ia_total = prev_counters.get("ia_total", 0.0)
    delta_fallback = ia_fallback - prev_ia_fallback
    delta_ia_total = ia_total - prev_ia_total
    rate_fallback = _compute_rate(delta_fallback, delta_ia_total)
    if rate_fallback > 10.0:
        _alert("ia_fallback_rate_high", rate_fallback, 10.0)
    prev_counters["ia_fallback"] = ia_fallback
    prev_counters["ia_total"] = ia_total


def _loop():
    registry = get_registry()
    prev_counters: Dict[str, float] = {}
    while True:
        time.sleep(ALERT_INTERVAL_SECONDS)
        try:
            _check_once(prev_counters)
        except Exception as exc:
            logger.warning({"event": "alerts_loop_error", "error": str(exc)})


def start_alert_loop():
    if os.getenv("PYTEST_CURRENT_TEST") or os.getenv("DISABLE_ALERTS") == "1":
        return
    t = threading.Thread(target=_loop, daemon=True)
    t.start()


# Test helper
def run_alert_check_once():
    _check_once({})
