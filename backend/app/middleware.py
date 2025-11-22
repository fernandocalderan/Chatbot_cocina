import json
import time
import uuid
from typing import Callable

from fastapi import Request
from starlette.responses import Response

from app.core.config import get_settings


class RateLimiter:
    def __init__(self, max_per_min: int):
        self.max_per_min = max_per_min
        self.bucket = {}

    def allow(self, key: str) -> bool:
        now = int(time.time() // 60)
        count, ts = self.bucket.get(key, (0, now))
        if ts != now:
            count, ts = 0, now
        count += 1
        self.bucket[key] = (count, ts)
        return count <= self.max_per_min


async def add_request_context(request: Request, call_next: Callable):
    settings = get_settings()
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    tenant_id = request.headers.get("X-Tenant-ID")
    request.state.tenant_id = tenant_id

    limiter = RateLimiter(settings.rate_limit_per_min)
    key = f"{tenant_id or 'anon'}:{request.client.host}"
    if not limiter.allow(key):
        return Response(
            content=json.dumps({"detail": "rate_limit_exceeded"}),
            media_type="application/json",
            status_code=429,
        )

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
