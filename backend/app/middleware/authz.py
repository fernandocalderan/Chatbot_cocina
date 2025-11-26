from typing import List, Optional

import jwt
from fastapi import Depends, Header, HTTPException, Request, status

from app.core.config import get_settings
from app.api.auth import oauth2_scheme
from app.services.key_manager import KeyManager
from app.services.jwt_blacklist import JWTBlacklist


class AuthzContext:
    def __init__(
        self,
        tenant_id: Optional[str],
        user_id: Optional[str],
        roles: List[str],
        token_type: str,
    ):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.roles = roles
        self.token_type = token_type


def decode_token(raw_token: str) -> AuthzContext:
    settings = get_settings()
    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="missing_token"
        )
    try:
        header = jwt.get_unverified_header(raw_token)
        kid = header.get("kid") or "current"
    except Exception:
        kid = "current"
    km = KeyManager()
    current_kid, current_secret, previous = km.get_jwt_keys()
    secrets_map = {current_kid: current_secret}
    secrets_map.update(previous)
    secret = secrets_map.get(kid)
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token"
        )
    try:
        payload = jwt.decode(raw_token, secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token"
        )
    jti = payload.get("jti")
    blacklist = JWTBlacklist(km.redis_url)
    if jti and blacklist.is_blacklisted(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="token_revoked"
        )
    token_type = payload.get("type", "access")
    tenant_id = payload.get("tenant_id")
    user_id = payload.get("sub")
    roles = payload.get("roles") or []
    if not isinstance(roles, list):
        roles = []
    return AuthzContext(
        tenant_id=tenant_id, user_id=user_id, roles=roles, token_type=token_type
    )


async def get_authz_context(
    token: str = Depends(oauth2_scheme), x_api_key: str | None = Header(default=None)
):
    settings = get_settings()
    # allow panel token bypass
    if settings.panel_api_token and x_api_key == settings.panel_api_token:
        return AuthzContext(
            tenant_id=None, user_id=None, roles=["ADMIN"], token_type="api_key"
        )
    return decode_token(token)


def require_role(role: str):
    async def _checker(
        ctx: AuthzContext = Depends(get_authz_context), request: Request = None
    ):
        if ctx.token_type == "widget":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="forbidden"
            )
        if role not in ctx.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="forbidden"
            )
        if request is not None and hasattr(request, "state"):
            request.state.user_id = ctx.user_id
            request.state.roles = ctx.roles
            if ctx.tenant_id:
                request.state.tenant_id = ctx.tenant_id

    return _checker


def require_any_role(*roles: str):
    async def _checker(
        ctx: AuthzContext = Depends(get_authz_context), request: Request = None
    ):
        if ctx.token_type == "widget":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="forbidden"
            )
        if roles and not any(r in ctx.roles for r in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="forbidden"
            )
        if request is not None and hasattr(request, "state"):
            request.state.user_id = ctx.user_id
            request.state.roles = ctx.roles
            if ctx.tenant_id:
                request.state.tenant_id = ctx.tenant_id

    return _checker
