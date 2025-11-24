from app.core.flow_engine import FlowEngine


def test_next_block_with_branch_match():
    flow = {"blocks": {"a": {"branches": {"yes": "b", "no": "c"}}}}
    engine = FlowEngine(flow)
    assert engine.next_block(flow["blocks"]["a"], "yes") == "b"
    assert engine.next_block(flow["blocks"]["a"], "unknown") in {"b", "c"}


def test_choose_text_prefers_lang_and_falls_back():
    flow = {"blocks": {"a": {"text": {"es": "hola", "en": "hi"}}}}
    engine = FlowEngine(flow)
    block = flow["blocks"]["a"]
    assert engine.choose_text(block, "en", "es") == "hi"
    assert engine.choose_text(block, "pt", "es") == "hola"


def test_next_block_default_branch():
    flow = {"blocks": {"a": {"branches": {"default": "b", "x": "c"}}}}
    engine = FlowEngine(flow)
    assert engine.next_block(flow["blocks"]["a"], "unknown") == "b"


def test_next_block_uses_next_when_no_branches():
    flow = {"blocks": {"a": {"next": "b"}, "b": {}}}
    engine = FlowEngine(flow)
    assert engine.next_block(flow["blocks"]["a"], "whatever") == "b"
    assert engine.next_block(flow["blocks"]["b"], "anything") is None


def test_choose_text_plain_and_empty():
    flow = {"blocks": {"a": {"text": "hola"}, "b": {}}}
    engine = FlowEngine(flow)
    assert engine.choose_text(flow["blocks"]["a"], "es", "es") == "hola"
    assert engine.choose_text(flow["blocks"]["b"], "es", "es") == ""
