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
