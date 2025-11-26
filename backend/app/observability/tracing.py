from __future__ import annotations

import contextvars
import uuid
from typing import Optional


_request_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)
_tenant_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "tenant_id", default=None
)
_session_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "session_id", default=None
)
_span_stack: contextvars.ContextVar[list[str]] = contextvars.ContextVar(
    "span_stack", default=[]
)


def set_request_context(
    request_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    session_id: Optional[str] = None,
):
    if request_id:
        _request_id.set(request_id)
    if tenant_id:
        _tenant_id.set(str(tenant_id))
    if session_id:
        _session_id.set(str(session_id))


def clear_request_context():
    _request_id.set(None)
    _tenant_id.set(None)
    _session_id.set(None)
    _span_stack.set([])


def get_request_id() -> Optional[str]:
    return _request_id.get()


def get_trace_context() -> dict:
    return {
        "request_id": _request_id.get(),
        "tenant_id": _tenant_id.get(),
        "session_id": _session_id.get(),
        "span": _span_stack.get()[-1] if _span_stack.get() else None,
    }


def start_span(name: str) -> str:
    stack = list(_span_stack.get() or [])
    span_id = f"{name}-{uuid.uuid4().hex[:8]}"
    stack.append(span_id)
    _span_stack.set(stack)
    return span_id


def end_span():
    stack = list(_span_stack.get() or [])
    if stack:
        stack.pop()
    _span_stack.set(stack)
