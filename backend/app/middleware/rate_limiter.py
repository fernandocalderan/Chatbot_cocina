import json
import time
import uuid
from typing import Callable

import redis
from fastapi import Request
from starlette.responses import Response

from app.core.config import get_settings


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
    tenant_id = request.headers.get("X-Tenant-ID")
    request.state.tenant_id = tenant_id

    key = f"rl:{tenant_id or 'anon'}:{request.client.host}"
    if not check_rate_limit(settings.redis_url, key, settings.rate_limit_per_min):
        return Response(
            content=json.dumps({"detail": "rate_limit_exceeded"}),
            media_type="application/json",
            status_code=429,
        )

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
