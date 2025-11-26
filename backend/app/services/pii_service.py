from __future__ import annotations

import base64
import os
import re
from dataclasses import dataclass
from typing import Dict, Optional

from cryptography.fernet import Fernet
from loguru import logger

try:
    import boto3
except Exception:
    boto3 = None

from app.services.key_manager import KeyManager


PII_PREFIX = "enc"
CURRENT_KEY_VERSION = 1


@dataclass
class PIIKeys:
    current_key: bytes
    legacy_keys: Dict[int, bytes]


class PIIService:
    def __init__(self):
        self.key_manager = KeyManager()
        self.keys = self._load_keys()

    def _load_keys(self) -> PIIKeys:
        legacy_keys: Dict[int, bytes] = {}
        key_bytes = self._load_current_key()
        legacy_env = os.getenv("PII_LEGACY_KEY")
        if legacy_env:
            try:
                legacy_keys[CURRENT_KEY_VERSION - 1] = legacy_env.encode()
            except Exception:
                pass
        try:
            current_external, legacy_external = self.key_manager.get_pii_keys()
            if current_external:
                key_bytes = self._normalize_key(
                    current_external.decode()
                    if isinstance(current_external, bytes)
                    else current_external
                )
            for k, v in legacy_external.items():
                legacy_keys[k] = self._normalize_key(
                    v.decode() if isinstance(v, bytes) else v
                )
        except Exception:
            pass
        return PIIKeys(current_key=key_bytes, legacy_keys=legacy_keys)

    def _load_current_key(self) -> bytes:
        # Intentar override desde KeyManager
        try:
            current_external, legacy_external = self.key_manager.get_pii_keys()
            if current_external:
                return self._normalize_key(
                    current_external.decode()
                    if isinstance(current_external, bytes)
                    else current_external
                )
        except Exception:
            pass
        secret_name = os.getenv("PII_SECRET_NAME")
        if secret_name and boto3:
            try:
                sm = boto3.client("secretsmanager")
                resp = sm.get_secret_value(SecretId=secret_name)
                secret_val = resp.get("SecretString") or ""
                if secret_val:
                    return self._normalize_key(secret_val)
            except Exception as exc:
                logger.warning(
                    {"event": "pii_secretmanager_fallback_env", "error": str(exc)}
                )
        env_key = os.getenv("PII_ENCRYPTION_KEY")
        if env_key:
            return self._normalize_key(env_key)
        # fallback dev key
        dev_key = base64.urlsafe_b64encode(os.urandom(32))
        logger.warning({"event": "pii_dev_key_generated"})
        return dev_key

    def _normalize_key(self, key_str: str) -> bytes:
        try:
            raw = key_str.encode()
            # if already base64 fernet-sized, return
            Fernet(raw)
            return raw
        except Exception:
            pass
        return base64.urlsafe_b64encode(key_str.encode().ljust(32, b"0")[:32])

    def _get_fernet(self, version: int) -> Optional[Fernet]:
        if version == CURRENT_KEY_VERSION:
            return Fernet(self.keys.current_key)
        if version in self.keys.legacy_keys:
            return Fernet(self.keys.legacy_keys[version])
        return None

    def encrypt_pii(
        self,
        value: Optional[str],
        field_name: str = "",
        tenant_id: Optional[str] = None,
    ) -> Optional[str]:
        if not value:
            return value
        if isinstance(value, str) and value.startswith(f"{PII_PREFIX}:"):
            return value
        f = self._get_fernet(CURRENT_KEY_VERSION)
        token = f.encrypt(value.encode()).decode()
        return f"{PII_PREFIX}:v{CURRENT_KEY_VERSION}:{token}"

    def decrypt_pii(self, ciphertext: Optional[str]) -> Optional[str]:
        if not ciphertext or not isinstance(ciphertext, str):
            return ciphertext
        if not ciphertext.startswith(f"{PII_PREFIX}:"):
            return ciphertext
        try:
            _, version_part, token = ciphertext.split(":", 2)
            version = int(version_part.replace("v", ""))
        except Exception:
            return ciphertext
        f = self._get_fernet(version)
        if not f:
            return ciphertext
        try:
            return f.decrypt(token.encode()).decode()
        except Exception:
            return ciphertext

    def mask_pii(self, value: Optional[str], field_name: str = "") -> Optional[str]:
        if not value:
            return value
        if "@" in value:
            parts = value.split("@", 1)
            return f"{self._mask_generic(parts[0])}@{parts[1]}"
        return self._mask_generic(value)

    def _mask_generic(self, value: str) -> str:
        if len(value) <= 4:
            return "*" * len(value)
        return f"{value[:2]}***{value[-2:]}"

    def is_encrypted(self, value: Optional[str]) -> bool:
        return bool(isinstance(value, str) and value.startswith(f"{PII_PREFIX}:v"))

    def contains_pii(self, text: str) -> bool:
        if not text:
            return False
        email_re = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
        phone_re = re.compile(r"\+?\d{7,}")
        return bool(email_re.search(text) or phone_re.search(text))

    def encrypt_meta(self, meta: dict, tenant_id: Optional[str]) -> tuple[dict, bool]:
        changed = False
        if not isinstance(meta, dict):
            return meta, changed
        fields = [
            "contact_name",
            "contact_email",
            "contact_phone",
            "contact_address",
            "address",
            "name",
        ]
        new_meta = dict(meta)
        for field in fields:
            val = new_meta.get(field)
            if isinstance(val, str) and not self.is_encrypted(val):
                new_meta[field] = self.encrypt_pii(
                    val, field_name=field, tenant_id=tenant_id
                )
                changed = True
        return new_meta, changed

    def decrypt_meta(self, meta: dict) -> dict:
        if not isinstance(meta, dict):
            return meta
        new_meta = dict(meta)
        for k, v in meta.items():
            if isinstance(v, str) and self.is_encrypted(v):
                new_meta[k] = self.decrypt_pii(v)
        return new_meta

    def encrypt_message_content(
        self, content: str, tenant_id: Optional[str]
    ) -> tuple[str, bool]:
        if not content:
            return content, False
        if self.is_encrypted(content):
            return content, False
        if self.contains_pii(content):
            return (
                self.encrypt_pii(content, field_name="content", tenant_id=tenant_id),
                True,
            )
        return content, False
