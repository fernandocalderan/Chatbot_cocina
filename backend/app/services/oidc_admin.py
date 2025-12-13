import time
from functools import lru_cache
from typing import Any, Optional

import requests
import jwt
from jwt import algorithms

from app.core.config import get_settings


class OIDCValidationError(Exception):
    pass


@lru_cache(maxsize=1)
def _fetch_openid_config(issuer: str) -> dict:
    resp = requests.get(f"{issuer.rstrip('/')}/.well-known/openid-configuration", timeout=5)
    resp.raise_for_status()
    return resp.json()


@lru_cache(maxsize=1)
def _fetch_jwks(jwks_uri: str) -> dict:
    resp = requests.get(jwks_uri, timeout=5)
    resp.raise_for_status()
    return resp.json()


def validate_admin_id_token(id_token: str) -> dict[str, Any]:
    settings = get_settings()
    if not settings.oidc_issuer or not settings.oidc_client_id:
        raise OIDCValidationError("oidc_not_configured")

    try:
        header = jwt.get_unverified_header(id_token)
        kid = header.get("kid")
    except Exception as exc:
        raise OIDCValidationError(f"invalid_header: {exc}") from exc

    try:
        cfg = _fetch_openid_config(settings.oidc_issuer)
        jwks_uri = cfg.get("jwks_uri")
        if not jwks_uri:
            raise OIDCValidationError("jwks_uri_not_found")
        jwks = _fetch_jwks(jwks_uri)
    except requests.RequestException as exc:
        raise OIDCValidationError(f"oidc_fetch_failed: {exc}") from exc

    keys = jwks.get("keys") or []
    jwk = next((k for k in keys if k.get("kid") == kid), None)
    if not jwk:
        raise OIDCValidationError("kid_not_found")
    public_key = algorithms.RSAAlgorithm.from_jwk(jwk)

    try:
        payload = jwt.decode(
            id_token,
            public_key,
            audience=settings.oidc_client_id,
            issuer=settings.oidc_issuer,
            algorithms=["RS256", "RS512", "RS384"],
        )
    except jwt.PyJWTError as exc:
        raise OIDCValidationError(f"invalid_token: {exc}") from exc

    exp = payload.get("exp")
    if exp and exp < int(time.time()):
        raise OIDCValidationError("token_expired")

    email = (payload.get("email") or "").lower()
    if settings.oidc_admin_allowed_domain:
        allowed_domain = settings.oidc_admin_allowed_domain.lower()
        if not email.endswith(f"@{allowed_domain}"):
            raise OIDCValidationError("email_domain_not_allowed")

    return payload
