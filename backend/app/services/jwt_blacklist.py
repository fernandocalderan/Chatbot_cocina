import time
from typing import Optional

import redis

from app.core.config import get_settings


class JWTBlacklist:
    _MEMORY: dict[str, float] = {}

    def __init__(self, redis_url: Optional[str] = None):
        settings = get_settings()
        self.redis_url = redis_url or settings.redis_url
        try:
            if self.redis_url.startswith("memory://"):
                self.redis = None
            else:
                self.redis = redis.from_url(self.redis_url)
        except Exception:
            self.redis = None

    def blacklist_token(self, jti: str, exp_timestamp: float):
        if not jti:
            return
        ttl = max(int(exp_timestamp - time.time()), 0)
        if self.redis:
            self.redis.setex(f"blacklist:{jti}", ttl, "1")
        else:
            self._MEMORY[jti] = time.time() + ttl

    def is_blacklisted(self, jti: str) -> bool:
        if not jti:
            return False
        if self.redis:
            return bool(self.redis.get(f"blacklist:{jti}"))
        expiry = self._MEMORY.get(jti)
        if expiry is None:
            return False
        if expiry < time.time():
            self._MEMORY.pop(jti, None)
            return False
        return True
