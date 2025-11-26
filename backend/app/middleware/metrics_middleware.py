import time
from typing import Callable

from fastapi import Request

from app.core.config import get_settings
from app.observability import metrics
from app.observability.tracing import set_request_context, clear_request_context


async def metrics_middleware(request: Request, call_next: Callable):
    settings = get_settings()
    start = time.perf_counter()
    tenant_id = getattr(request.state, "tenant_id", None)
    request_id = getattr(request.state, "request_id", None)
    set_request_context(
        request_id=request_id,
        tenant_id=tenant_id,
        session_id=getattr(request.state, "session_id", None),
    )
    response = await call_next(request)
    duration = time.perf_counter() - start
    labels = {
        "path": request.url.path,
        "method": request.method,
        "status_code": getattr(response, "status_code", 0),
        "tenant_id": tenant_id or "unknown",
    }
    metrics.inc_counter("api_requests_total", labels)
    metrics.observe_histogram(
        "api_latency_seconds",
        duration,
        {"path": request.url.path, "method": request.method, "tenant_id": tenant_id or "unknown"},
    )
    clear_request_context()
    return response
