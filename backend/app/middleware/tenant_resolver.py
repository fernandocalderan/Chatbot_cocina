import os
import uuid
import datetime
from typing import Callable

import jwt
from fastapi import Request
from starlette.responses import JSONResponse

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.tenants import Tenant
from app.models.users import User


def _origin_allowed(
    origin: str, referer: str, allowed_origins: list[str] | None
) -> bool:
    if not allowed_origins:
        return True
    for allowed in allowed_origins:
        if not allowed:
            continue
        if origin.startswith(allowed) or referer.startswith(allowed):
            return True
    return False


def _safe_uuid(value: str | None) -> str | None:
    """
    Normaliza y valida UUIDs recibidos por cabecera/payload.
    Devuelve None si el valor no es un UUID válido.
    """
    if not value:
        return None
    try:
        return str(uuid.UUID(str(value)))
    except (ValueError, AttributeError, TypeError):
        return None


async def resolve_tenant(request: Request, call_next: Callable):
    """
    Resuelve tenant_id a partir de:
    - x-api-key que coincida con PANEL_API_TOKEN -> primer tenant disponible.
    - JWT Bearer -> sub = user.id -> tenant_id del usuario.
    Si no se puede resolver un tenant válido, devuelve 401.
    """
    # Permitir bypass en modo sin DB (tests locales)
    if os.getenv("DISABLE_DB") == "1":
        request.state.tenant_id = request.headers.get("X-Tenant-ID") or "test-tenant"
        return await call_next(request)

    settings = get_settings()
    api_key = request.headers.get("x-api-key") or request.headers.get("X-Api-Key")
    header_tenant_raw = request.headers.get("X-Tenant-ID") or request.headers.get(
        "x-tenant-id"
    )
    header_tenant = _safe_uuid(header_tenant_raw)
    if header_tenant_raw and not header_tenant:
        return JSONResponse({"detail": "invalid_tenant_id"}, status_code=400)
    auth_header = request.headers.get("Authorization", "")
    token_bearer = (
        auth_header.split(" ", 1)[1]
        if auth_header.lower().startswith("bearer ")
        else None
    )
    admin_api_token = settings.admin_api_token
    tenant_id = None
    tenant_obj = None
    token_type = None
    roles = []
    allowed_origin_claim = None
    impersonate_tenant_id = None

    db = SessionLocal()
    try:
        # Bypass para API key de superadmin (no requiere tenant)
        if admin_api_token and api_key and api_key == admin_api_token:
            request.state.tenant_id = None
            request.state.token_type = "ADMIN"
            request.state.roles = ["SUPER_ADMIN"]
            return await call_next(request)

        # Prioriza header explícito de tenant si llega
        if header_tenant:
            tenant_obj = db.query(Tenant).filter(Tenant.id == header_tenant).first()
            if not tenant_obj:
                return JSONResponse({"detail": "tenant_not_found"}, status_code=401)
            tenant_id = str(tenant_obj.id)
        elif (
            api_key and settings.panel_api_token and api_key == settings.panel_api_token
        ):
            tenant_obj = db.query(Tenant).first()
            if not tenant_obj:
                return JSONResponse({"detail": "tenant_not_found"}, status_code=401)
            tenant_id = str(tenant_obj.id)
        elif token_bearer and settings.jwt_secret:
            from app.services.key_manager import KeyManager
            from app.services.jwt_blacklist import JWTBlacklist

            km = KeyManager()
            try:
                header = jwt.get_unverified_header(token_bearer)
                kid = header.get("kid") or "current"
            except Exception:
                kid = "current"
            current_kid, current_secret, previous = km.get_jwt_keys()
            secrets_map = {current_kid: current_secret}
            secrets_map.update(previous)
            secret = secrets_map.get(kid)
            if not secret:
                return JSONResponse({"detail": "invalid_token"}, status_code=401)
            try:
                payload = jwt.decode(
                    token_bearer, secret, algorithms=[settings.jwt_algorithm]
                )
            except jwt.PyJWTError:
                return JSONResponse({"detail": "invalid_token"}, status_code=401)
            jti = payload.get("jti")
            if jti and JWTBlacklist(km.redis_url).is_blacklisted(jti):
                return JSONResponse({"detail": "invalid_token"}, status_code=401)
            token_type = (payload.get("type") or "").upper()
            roles_raw = payload.get("roles") or []
            roles = [str(r).upper() for r in roles_raw] if isinstance(roles_raw, list) else []
            impersonate_tenant_id = payload.get("impersonate_tenant_id")
            if token_type == "ADMIN" or "SUPER_ADMIN" in roles:
                request.state.tenant_id = None
                request.state.token_type = token_type
                request.state.roles = roles
                return await call_next(request)
            if token_type == "WIDGET":
                allowed_origin_claim = payload.get("allowed_origin")
                allowed = payload.get("allowed_origin")
                token_iat = payload.get("iat")
                origin = (
                    request.headers.get("Origin") or request.headers.get("origin") or ""
                )
                referer = (
                    request.headers.get("Referer")
                    or request.headers.get("referer")
                    or ""
                )
                if not allowed:
                    return JSONResponse(
                        {"detail": "origin_not_allowed"}, status_code=401
                    )
                if not origin and not referer:
                    return JSONResponse({"detail": "origin_required"}, status_code=401)
                if not (origin.startswith(allowed) or referer.startswith(allowed)):
                    return JSONResponse(
                        {"detail": "origin_not_allowed"}, status_code=401
                    )
                tenant_id = _safe_uuid(payload.get("tenant_id"))
                if not tenant_id:
                    return JSONResponse({"detail": "tenant_not_found"}, status_code=401)
                if tenant_id and tenant_obj is None:
                    tenant_obj = db.query(Tenant).filter(Tenant.id == tenant_id).first()
                revoked_before = None
                if tenant_obj:
                    branding = getattr(tenant_obj, "branding", {}) or {}
                    revoked_before = branding.get("widget_tokens_revoked_before")
                if revoked_before and token_iat:
                    try:
                        revoked_dt = datetime.datetime.fromisoformat(revoked_before)
                        issued_dt = datetime.datetime.fromtimestamp(int(token_iat), datetime.timezone.utc)
                        if issued_dt < revoked_dt:
                            return JSONResponse({"detail": "token_revoked"}, status_code=401)
                    except Exception:
                        pass
            elif impersonate_tenant_id:
                tenant_id = _safe_uuid(impersonate_tenant_id)
                if not tenant_id:
                    return JSONResponse({"detail": "tenant_not_found"}, status_code=401)
            else:
                user_id = payload.get("sub")
                if not user_id:
                    return JSONResponse({"detail": "invalid_token"}, status_code=401)
                user = db.query(User).filter(User.id == user_id).first()
                if not user or not user.tenant_id:
                    return JSONResponse({"detail": "tenant_not_found"}, status_code=401)
                tenant_id = str(user.tenant_id)
                tenant_obj = db.query(Tenant).filter(Tenant.id == tenant_id).first()

        if (api_key or token_bearer) and not tenant_id:
            return JSONResponse({"detail": "tenant_not_found"}, status_code=401)

        # Whitelist de origen por tenant (branding.allowed_origins)
        if tenant_id and not tenant_obj:
            tenant_obj = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        origin = request.headers.get("Origin") or request.headers.get("origin") or ""
        referer = request.headers.get("Referer") or request.headers.get("referer") or ""
        allowed_origins = []
        if tenant_obj:
            branding = getattr(tenant_obj, "branding", {}) or {}
            allowed_origins = (
                branding.get("allowed_widget_origins")
                or branding.get("allowed_origins")
                or branding.get("allowedOrigins")
                or []
            )
            if allowed_origin_claim and allowed_origin_claim not in allowed_origins:
                allowed_origins.append(allowed_origin_claim)
            maintenance_flag = (
                branding.get("maintenance_mode")
                or branding.get("maintenance")
                or False
            )
            request.state.tenant_maintenance = bool(maintenance_flag)
        if (
            (origin or referer)
            and tenant_obj
            and not _origin_allowed(origin, referer, allowed_origins)
        ):
            return JSONResponse({"detail": "origin_not_allowed"}, status_code=401)

        request.state.tenant_id = tenant_id
        request.state.token_type = token_type
        request.state.roles = roles
        if tenant_obj:
            request.state.tenant_obj = tenant_obj
    finally:
        db.close()

    return await call_next(request)
