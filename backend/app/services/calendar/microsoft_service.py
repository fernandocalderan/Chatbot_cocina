from __future__ import annotations

import time
import uuid
from typing import Any, Dict, Optional

import redis
from loguru import logger

from app.core.config import get_settings


class MicrosoftCalendarService:
    def __init__(self, tenant: Any, redis_url: Optional[str] = None):
        self.tenant = tenant
        self.settings = get_settings()
        self.redis = None
        try:
            self.redis = redis.from_url(redis_url or self.settings.redis_url)
        except Exception:
            self.redis = None
        self.refresh_token = getattr(tenant, "microsoft_refresh_token", None)
        self.calendar_id = getattr(tenant, "microsoft_calendar_id", None)

    def _allowed(self) -> bool:
        return bool(self.refresh_token)

    def _rate_limit(self) -> bool:
        if not self.redis:
            return True
        try:
            key = (
                f"tenant:{getattr(self.tenant, 'id', 'unknown')}:calendar_rl_microsoft"
            )
            pipe = self.redis.pipeline()
            pipe.incr(key, 1)
            pipe.expire(key, 60)
            count, _ = pipe.execute()
            return count <= 10
        except Exception:
            return True

    def _log(
        self,
        operation: str,
        success: bool,
        latency_ms: float,
        external_event_id: Optional[str] = None,
        appointment_id: Optional[str] = None,
    ):
        logger.info(
            {
                "tenant_id": str(getattr(self.tenant, "id", None)),
                "provider": "microsoft",
                "operation": operation,
                "appointment_id": appointment_id,
                "external_event_id": external_event_id,
                "success": success,
                "latency_ms": round(latency_ms, 2),
            }
        )

    def create_event(self, appointment: Any) -> Dict[str, Any]:
        start = time.perf_counter()
        if not self._allowed() or not self._rate_limit():
            self._log(
                "create_event",
                False,
                0.0,
                appointment_id=str(getattr(appointment, "id", None)),
            )
            return {"success": False}
        try:
            external_id = str(uuid.uuid4())
            latency = (time.perf_counter() - start) * 1000
            self._log(
                "create_event",
                True,
                latency,
                external_event_id=external_id,
                appointment_id=str(getattr(appointment, "id", None)),
            )
            return {"success": True, "event_id": external_id}
        except Exception:
            self._log(
                "create_event",
                False,
                (time.perf_counter() - start) * 1000,
                appointment_id=str(getattr(appointment, "id", None)),
            )
            return {"success": False}

    def delete_event(self, event_id: str) -> Dict[str, Any]:
        start = time.perf_counter()
        if not self._allowed() or not self._rate_limit():
            self._log("delete_event", False, 0.0, external_event_id=event_id)
            return {"success": False}
        try:
            latency = (time.perf_counter() - start) * 1000
            self._log("delete_event", True, latency, external_event_id=event_id)
            return {"success": True}
        except Exception:
            self._log(
                "delete_event",
                False,
                (time.perf_counter() - start) * 1000,
                external_event_id=event_id,
            )
            return {"success": False}

    def list_events(self, start_iso: str, end_iso: str) -> Dict[str, Any]:
        start = time.perf_counter()
        if not self._allowed() or not self._rate_limit():
            self._log("list_events", False, 0.0)
            return {"success": False, "events": []}
        try:
            latency = (time.perf_counter() - start) * 1000
            self._log("list_events", True, latency)
            return {"success": True, "events": []}
        except Exception:
            self._log("list_events", False, (time.perf_counter() - start) * 1000)
            return {"success": False, "events": []}
