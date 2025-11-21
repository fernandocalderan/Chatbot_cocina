import json
from typing import Any

import redis


class SessionManager:
    _GLOBAL_MEMORY: dict[str, Any] = {}

    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        if redis_url.startswith("memory://"):
            self.backend = "memory"
            self._store = self._GLOBAL_MEMORY
            self.r = None
        else:
            self.backend = "redis"
            self.r = redis.from_url(redis_url)

    def load(self, session_id: str):
        if self.backend == "memory":
            return self._store.get(session_id, {})
        data = self.r.get(session_id)
        return json.loads(data) if data else {}

    def save(self, session_id: str, state: dict):
        if self.backend == "memory":
            self._store[session_id] = state
            return
        self.r.set(session_id, json.dumps(state))
