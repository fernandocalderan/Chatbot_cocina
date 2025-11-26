import os
from pathlib import Path

from loguru import logger

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


def setup_logger():
    logger.remove()

    def _mask_record(record):
        ctx = get_trace_context()
        msg = record["message"]
        if isinstance(msg, dict):
            msg = {**ctx, **msg}
        record["message"] = mask_payload(msg)
        return record

    logger.configure(patcher=_mask_record)
    log_path = LOG_DIR / "app.log"
    logger.add(
        log_path,
        rotation="10 MB",
        retention="7 days",
        serialize=True,
        format="{time} | {level} | {message}",
    )
    logger.add(
        sink=lambda msg: print(msg, end=""),
        format="{time} | {level} | {message}",
    )
    return logger
