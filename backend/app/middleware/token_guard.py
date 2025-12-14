import jwt
from fastapi import Request
from starlette.responses import JSONResponse

from app.core.config import get_settings
from app.middleware.authz import decode_token


async def admin_token_guard(request: Request, call_next):
    """
    Bloquea el uso de tokens ADMIN/SUPER_ADMIN en rutas de producto (chat/widget/flows)
    y bloquea tokens WIDGET en rutas de administración.
    """
    path = request.url.path or ""
    settings = get_settings()

    # Detectar admin api key (bypass OIDC)
    admin_api_key = settings.admin_api_token
    panel_api_key = settings.panel_api_token
    x_api_key = request.headers.get("x-api-key")
    is_admin_api_key = admin_api_key and x_api_key == admin_api_key
    is_panel_api_key = panel_api_key and x_api_key == panel_api_key

    raw_token = None
    auth_header = request.headers.get("Authorization") or request.headers.get("authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        raw_token = auth_header.split(" ", 1)[1].strip()

    token_type = None
    roles = []
    if raw_token:
        try:
            ctx = decode_token(raw_token)
            token_type = ctx.token_type
            roles = ctx.roles or []
        except Exception:
            # Si el token es inválido, dejar que el flujo normal lo rechace en auth
            token_type = None

    # Bloquear admin tokens o admin_api_key en chat/widget/flows
    if path.startswith("/v1/chat") or path.startswith("/v1/widget") or path.startswith("/v1/flows"):
        if is_admin_api_key or (token_type == "ADMIN" or "SUPER_ADMIN" in roles):
            return JSONResponse(
                {"detail": "admin_token_not_allowed"},
                status_code=403,
            )

    # Bloquear widgets en admin
    if path.startswith("/v1/admin"):
        if token_type == "WIDGET" or is_panel_api_key:
            return JSONResponse(
                {"detail": "forbidden"},
                status_code=403,
            )

    response = await call_next(request)
    return response
