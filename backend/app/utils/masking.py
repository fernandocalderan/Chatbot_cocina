import re
from typing import Any, Dict


EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\+?\d[\d\s\-]{6,}\d")
ID_RE = re.compile(r"\b(\d{8}[A-Za-z]|[A-Za-z]\d{7})\b")


def mask_text(value: str) -> str:
    if not value:
        return value
    masked = EMAIL_RE.sub("***@***", value)
    masked = PHONE_RE.sub("********", masked)
    masked = ID_RE.sub("***", masked)
    return masked


def mask_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    safe = {}
    for key, val in data.items():
        if isinstance(val, str):
            safe[key] = mask_text(val)
        elif isinstance(val, dict):
            safe[key] = mask_dict(val)
        else:
            safe[key] = val
    return safe


def mask_payload(payload: Any) -> Any:
    if isinstance(payload, str):
        return mask_text(payload)
    if isinstance(payload, dict):
        return mask_dict(payload)
    return payload
