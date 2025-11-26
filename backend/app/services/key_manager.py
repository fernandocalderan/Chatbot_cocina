from __future__ import annotations

import json
from typing import Dict, Optional, Tuple

import redis

from app.core.config import get_settings


class KeyManager:
    def __init__(self, redis_url: Optional[str] = None):
        self.settings = get_settings()
        self.redis_url = redis_url or self.settings.redis_url
        try:
            if self.redis_url.startswith("memory://"):
                self.redis = None
            else:
                self.redis = redis.from_url(self.redis_url)
        except Exception:
            self.redis = None

    # ---------- JWT keys ----------
    def get_jwt_keys(self) -> Tuple[str, str, Dict[str, str]]:
        current_kid = self.settings.jwt_key_current_id or "current"
        current_secret = (
            self._get_redis_key("keys:jwt:current")
            or self.settings.jwt_private_key_current
            or self.settings.jwt_secret
        )
        previous_raw = (
            self._get_redis_key("keys:jwt:previous")
            or self.settings.jwt_private_key_previous
        )
        previous = {}
        if previous_raw:
            try:
                previous = (
                    json.loads(previous_raw)
                    if isinstance(previous_raw, str) and previous_raw.startswith("{")
                    else {"previous": previous_raw}
                )
            except Exception:
                previous = {"previous": previous_raw}
        return current_kid, current_secret, previous

    def rotate_jwt_keys(self, new_kid: str, new_secret: str):
        if not self.redis:
            return
        _, current_secret, prev_map = self.get_jwt_keys()
        if current_secret:
            prev_map["previous"] = current_secret
        self.redis.set("keys:jwt:previous", json.dumps(prev_map))
        self.redis.set("keys:jwt:current", new_secret)
        self.redis.set("keys:jwt:kid", new_kid)

    # ---------- PII keys ----------
    def get_pii_keys(self) -> Tuple[bytes, Dict[int, bytes]]:
        current = (
            self._get_redis_key("keys:pii:current")
            or self.settings.pii_key_current
            or self.settings.pii_encryption_key
            or self.settings.jwt_secret
            or ""
        )
        previous_raw = (
            self._get_redis_key("keys:pii:previous") or self.settings.pii_key_previous
        )
        legacy = {}
        if previous_raw:
            try:
                legacy_json = (
                    json.loads(previous_raw)
                    if isinstance(previous_raw, str) and previous_raw.startswith("{")
                    else {}
                )
            except Exception:
                legacy_json = {}
            if isinstance(legacy_json, dict) and legacy_json:
                for k, v in legacy_json.items():
                    try:
                        legacy[int(k)] = v.encode() if isinstance(v, str) else v
                    except Exception:
                        continue
            elif isinstance(previous_raw, str):
                legacy[0] = previous_raw.encode()
        return (
            current.encode() if isinstance(current, str) else current,
            legacy,
        )

    def rotate_pii_keys(self, new_key: str):
        if not self.redis:
            return
        current, legacy = self.get_pii_keys()
        legacy_map = {
            **legacy,
            0: (
                current.decode()
                if isinstance(current, (bytes, bytearray))
                else str(current)
            ),
        }
        self.redis.set("keys:pii:previous", json.dumps(legacy_map))
        self.redis.set("keys:pii:current", new_key)

    # ---------- helpers ----------
    def _get_redis_key(self, key: str) -> Optional[str]:
        if not self.redis:
            return None
        val = self.redis.get(key)
        return val.decode() if isinstance(val, (bytes, bytearray)) else val
