from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from app.core.config import get_settings
from app.utils.masking import mask_text


BLOCK_PATTERNS = [
    re.compile(pat, re.IGNORECASE)
    for pat in [
        r"terrorism",
        r"bomb|explosive",
        r"violencia extrema",
        r"abuso infantil",
        r"contenido sexual.*menor",
        r"odio racial",
        r"\bkill\b",
        r"arma[s]?",
    ]
]

SENSITIVE_PATTERNS = [
    re.compile(r"\b(dni|nie|pasaporte|passport)\b", re.IGNORECASE),
    re.compile(r"\b(tarjeta de cr[eé]dito|credit card)\b", re.IGNORECASE),
]


@dataclass
class ModerationDecision:
    allowed: bool
    reason: Optional[str] = None
    masked_text: Optional[str] = None


class AIModeration:
    def __init__(self):
        self.settings = get_settings()

    def enabled(self) -> bool:
        return bool(self.settings.ai_moderation_enabled)

    def check_input(self, text: str) -> ModerationDecision:
        if not self.enabled():
            return ModerationDecision(allowed=True, masked_text=text)
        if not text:
            return ModerationDecision(allowed=True, masked_text=text)
        masked = mask_text(text)
        for pattern in BLOCK_PATTERNS:
            if pattern.search(text):
                return ModerationDecision(
                    allowed=False, reason="blocked_input", masked_text=masked
                )
        if self.settings.ai_moderation_strict_mode:
            for pattern in SENSITIVE_PATTERNS:
                if pattern.search(text):
                    return ModerationDecision(
                        allowed=False, reason="sensitive_input", masked_text=masked
                    )
        return ModerationDecision(allowed=True, masked_text=masked)

    def check_output(self, text: str) -> ModerationDecision:
        if not self.enabled():
            return ModerationDecision(allowed=True, masked_text=text)
        if not text:
            return ModerationDecision(allowed=True, masked_text=text)
        masked = mask_text(text)
        for pattern in BLOCK_PATTERNS:
            if pattern.search(text):
                return ModerationDecision(
                    allowed=False, reason="blocked_output", masked_text=masked
                )
        return ModerationDecision(allowed=True, masked_text=masked)

