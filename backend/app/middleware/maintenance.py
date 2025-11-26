from fastapi import Request
from starlette.responses import JSONResponse

from app.core.config import get_settings


async def maintenance_guard(request: Request, call_next):
    settings = get_settings()
    path = request.url.path or ""
    # Allow health endpoints always
    if path.startswith("/v1/health"):
        return await call_next(request)

    global_maintenance = bool(settings.maintenance_mode)
    tenant_maintenance = bool(getattr(request.state, "tenant_maintenance", False))
    maintenance_on = global_maintenance or tenant_maintenance

    widget_route = path.startswith("/v1/chat")

    if maintenance_on and widget_route:
        message = getattr(settings, "maintenance_message", None) or "Mantenimiento en curso. Vuelve en unos minutos."
        return JSONResponse(
            status_code=503,
            content={"detail": "maintenance", "message": message},
        )

    return await call_next(request)
