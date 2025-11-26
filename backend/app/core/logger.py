import os
from pathlib import Path
from typing import Any, Dict

from loguru import logger
from app.core.config import get_settings

LOG_DIR = Path(__file__).resolve().parents[2] / "app" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

try:
    from app.utils.masking import mask_payload
except Exception:
    def mask_payload(payload):
        return payload

try:
    from app.observability.tracing import get_trace_context
except Exception:
    def get_trace_context():
        return {}


def _configure_exporters(base_logger):
    settings = get_settings()
    exporter = (settings.log_exporter or "").lower()
    if exporter == "loki" and settings.loki_endpoint:
        try:
            from app.observability.exporters.loki_exporter import loki_sink

            base_logger.add(
                loki_sink(settings.loki_endpoint, settings.loki_basic_auth),
                serialize=True,
                backtrace=False,
                diagnose=False,
            )
        except Exception:
            pass
    if exporter == "cloudwatch" and settings.cloudwatch_log_group:
        try:
            from app.observability.exporters.cloudwatch_exporter import cloudwatch_sink

            base_logger.add(
                cloudwatch_sink(
                    settings.cloudwatch_log_group, settings.cloudwatch_log_stream
                ),
                serialize=True,
                backtrace=False,
                diagnose=False,
            )
        except Exception:
            pass


def setup_logger():
    logger.remove()

    def _mask_record(record):
        ctx = get_trace_context()
        msg = record["message"]
        payload: Dict[str, Any]
        if isinstance(msg, dict):
            payload = {**ctx, **msg}
        else:
            payload = {**ctx, "message": msg}
        record["message"] = mask_payload(payload)
        return record

    logger.configure(patcher=_mask_record)
    log_path = LOG_DIR / "app.log"
    logger.add(
        log_path,
        rotation="10 MB",
        retention="7 days",
        serialize=True,
        backtrace=False,
        diagnose=False,
    )
    logger.add(
        sink=lambda msg: print(msg, end=""),
        serialize=True,
        backtrace=False,
        diagnose=False,
    )
    _configure_exporters(logger)
    return logger
