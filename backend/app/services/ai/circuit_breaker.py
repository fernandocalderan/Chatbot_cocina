from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

import redis

from app.core.config import get_settings


@dataclass
class BreakerState:
    open: bool
    remaining_cooldown: int


class AICircuitBreaker:
    def __init__(
        self,
        redis_url: Optional[str] = None,
        threshold: Optional[int] = None,
        window_seconds: Optional[int] = None,
        cooldown_seconds: Optional[int] = None,
    ):
        settings = get_settings()
        self.redis_url = redis_url or settings.redis_url
        self.threshold = threshold or settings.ai_circuit_breaker_threshold
        self.window = window_seconds or settings.ai_circuit_breaker_window_seconds
        self.cooldown = cooldown_seconds or settings.ai_circuit_breaker_cooldown_seconds
        try:
            self.redis = (
                None if self.redis_url.startswith("memory://") else redis.from_url(self.redis_url)
            )
        except Exception:
            self.redis = None

    def _keys(self, tenant_key: str):
        safe = tenant_key or "global"
        return (
            f"cb:{safe}:errors",
            f"cb:{safe}:open",
        )

    def is_open(self, tenant_key: str) -> BreakerState:
        if not self.redis:
            return BreakerState(open=False, remaining_cooldown=0)
        _, open_key = self._keys(tenant_key)
        ttl = self.redis.ttl(open_key)
        return BreakerState(open=ttl and ttl > 0, remaining_cooldown=max(ttl or 0, 0))

    def record_failure(self, tenant_key: str):
        if not self.redis:
            return
        errors_key, open_key = self._keys(tenant_key)
        pipe = self.redis.pipeline()
        pipe.incr(errors_key, 1)
        pipe.expire(errors_key, self.window)
        count, _ = pipe.execute()
        if int(count) >= self.threshold:
            self.redis.set(open_key, "1", ex=self.cooldown)

    def record_success(self, tenant_key: str):
        if not self.redis:
            return
        errors_key, _ = self._keys(tenant_key)
        self.redis.delete(errors_key)

