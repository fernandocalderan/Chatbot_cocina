from app.observability.tracing import set_request_context, get_trace_context, start_span, end_span


def test_tracing_context_propagation():
    set_request_context(request_id="req-1", tenant_id="t1", session_id="s1")
    span = start_span("test")
    ctx = get_trace_context()
    assert ctx["request_id"] == "req-1"
    assert ctx["tenant_id"] == "t1"
    assert ctx["session_id"] == "s1"
    assert ctx["span"] == span
    end_span()
