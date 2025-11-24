import json
import time
from typing import Any

import redis


class IdempotencyStore:
    _MEMORY: dict[str, dict[str, Any]] = {}

    def __init__(self, redis_url: str, namespace: str = "idemp"):
        self.redis_url = redis_url
        self.namespace = namespace
        if redis_url.startswith("memory://"):
            self.backend = "memory"
            self._store = self._MEMORY
            self.r = None
        else:
            self.backend = "redis"
            self._store = None
            self.r = redis.from_url(redis_url)

    def _key(self, key: str) -> str:
        return f"{self.namespace}:{key}"

    def get(self, key: str) -> Any | None:
        full_key = self._key(key)
        if self.backend == "memory":
            entry = self._store.get(full_key)
            if not entry:
                return None
            expires_at = entry.get("expires_at")
            if expires_at and expires_at < time.time():
                self._store.pop(full_key, None)
                return None
            return entry.get("value")
        data = self.r.get(full_key)
        return json.loads(data) if data else None

    def set(self, key: str, value: Any, ttl_seconds: int = 86_400):
        full_key = self._key(key)
        if self.backend == "memory":
            self._store[full_key] = {"value": value, "expires_at": time.time() + ttl_seconds}
            return
        self.r.setex(full_key, ttl_seconds, json.dumps(value))
