from __future__ import annotations

import os
from typing import Optional

from loguru import logger

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.ai_interaction import AIInteractionAudit
from app.utils.masking import mask_payload


class AIAuditService:
    def __init__(self):
        self.settings = get_settings()

    def record(
        self,
        *,
        tenant_id: Optional[str],
        flow: str,
        user_input: Optional[str],
        ai_output: Optional[str],
        moderation_blocked: bool = False,
        moderation_adjusted: bool = False,
        circuit_breaker: bool = False,
        latency_ms: float | None = None,
    ):
        if os.getenv("DISABLE_DB") == "1" or (
            self.settings.environment == "local"
            and self.settings.redis_url.startswith("memory://")
        ):
            # tests often run without DB; avoid failing hard
            try:
                logger.info(
                    {
                        "event": "ai_audit",
                        "tenant_id": tenant_id,
                        "flow": flow,
                        "moderation_blocked": moderation_blocked,
                        "moderation_adjusted": moderation_adjusted,
                        "circuit_breaker": circuit_breaker,
                        "latency_ms": latency_ms,
                    }
                )
            except Exception:
                pass
            return
        try:
            db = SessionLocal()
            entry = AIInteractionAudit(
                tenant_id=str(tenant_id) if tenant_id else None,
                flow=flow,
                input_masked=mask_payload(user_input),
                output_masked=mask_payload(ai_output),
                moderation_blocked=moderation_blocked,
                moderation_adjusted=moderation_adjusted,
                circuit_breaker=circuit_breaker,
                latency_ms=latency_ms,
            )
            db.add(entry)
            db.commit()
        except Exception as exc:
            try:
                logger.warning({"event": "ai_audit_failed", "error": str(exc)})
            except Exception:
                pass
        finally:
            try:
                db.close()
            except Exception:
                pass
