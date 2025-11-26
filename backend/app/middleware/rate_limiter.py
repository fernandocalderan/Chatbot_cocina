import json
import time
import uuid
from typing import Callable

import redis
from fastapi import Request
from starlette.responses import Response

from app.core.config import get_settings
from app.observability.tracing import set_request_context


def check_rate_limit(redis_url: str, key: str, limit_per_min: int) -> bool:
    try:
        r = redis.from_url(redis_url)
        pipe = r.pipeline()
        pipe.incr(key, 1)
        pipe.expire(key, 60)
        count, _ = pipe.execute()
        return int(count) <= limit_per_min
    except Exception:
        # Si falla Redis, no bloqueamos.
        return True


async def add_request_context(request: Request, call_next: Callable):
    settings = get_settings()
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    tenant_id = getattr(request.state, "tenant_id", None) or request.headers.get("X-Tenant-ID")
    request.state.tenant_id = tenant_id

    client_ip = request.client.host if request.client else "unknown"
    path = request.url.path
    set_request_context(request_id=request_id, tenant_id=tenant_id, session_id=None)

    limits: list[tuple[str, int]] = []
    # Límite general por tenant (si hay tenant resuelto)
    if tenant_id:
        limits.append((f"rl:tenant:{tenant_id}", settings.rate_limit_chat_per_tenant))
    # Límite por IP para el widget (chat endpoints)
    if path.startswith("/v1/chat"):
        limits.append((f"rl:ip:{client_ip}:chat", settings.rate_limit_chat_per_ip))
    # Límite estricto para endpoints sensibles (reservas)
    if path == "/v1/appointments/book":
        limits.append((f"rl:tenant:{tenant_id or 'anon'}:appt", 10))
        limits.append((f"rl:ip:{client_ip}:appt", 10))
    if path.startswith("/v1/widget/token"):
        limits.append(
            (
                f"rl:tenant:{tenant_id or 'anon'}:widget_token",
                settings.rate_limit_widget_per_tenant,
            )
        )

    for key, limit in limits:
        if not check_rate_limit(settings.redis_url, key, limit):
            return Response(
                content=json.dumps({"detail": "rate_limit_exceeded"}),
                media_type="application/json",
                status_code=429,
            )

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
