import os
from typing import Callable

import jwt
from fastapi import Request
from starlette.responses import JSONResponse

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.tenants import Tenant
from app.models.users import User


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
    header_tenant = request.headers.get("X-Tenant-ID") or request.headers.get("x-tenant-id")
    auth_header = request.headers.get("Authorization", "")
    token_bearer = auth_header.split(" ", 1)[1] if auth_header.lower().startswith("bearer ") else None
    tenant_id = None

    db = SessionLocal()
    try:
        # Prioriza header explícito de tenant si llega
        if header_tenant:
            tenant = db.query(Tenant).filter(Tenant.id == header_tenant).first()
            if not tenant:
                return JSONResponse({"detail": "tenant_not_found"}, status_code=401)
            tenant_id = str(tenant.id)
        elif api_key and settings.panel_api_token and api_key == settings.panel_api_token:
            tenant = db.query(Tenant).first()
            if not tenant:
                return JSONResponse({"detail": "tenant_not_found"}, status_code=401)
            tenant_id = str(tenant.id)
        elif token_bearer and settings.jwt_secret:
            try:
                payload = jwt.decode(token_bearer, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
            except jwt.PyJWTError:
                return JSONResponse({"detail": "invalid_token"}, status_code=401)
            token_type = payload.get("type")
            if token_type == "widget":
                allowed = payload.get("allowed_origin")
                origin = request.headers.get("Origin") or request.headers.get("origin") or ""
                referer = request.headers.get("Referer") or request.headers.get("referer") or ""
                if not allowed:
                    return JSONResponse({"detail": "origin_not_allowed"}, status_code=401)
                if not origin and not referer:
                    return JSONResponse({"detail": "origin_required"}, status_code=401)
                if not (origin.startswith(allowed) or referer.startswith(allowed)):
                    return JSONResponse({"detail": "origin_not_allowed"}, status_code=401)
                tenant_id = payload.get("tenant_id")
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

        if (api_key or token_bearer) and not tenant_id:
            return JSONResponse({"detail": "tenant_not_found"}, status_code=401)

        request.state.tenant_id = tenant_id
    finally:
        db.close()

    return await call_next(request)
