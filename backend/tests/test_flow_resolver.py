from __future__ import annotations

from pathlib import Path

from app.services.flow_resolver import resolve_flow_for_scope


def test_resolve_flow_for_scope_returns_base():
    flow, source = resolve_flow_for_scope("kitchens", None)
    assert isinstance(flow, dict)
    assert source is None or source.endswith("flow_base.json")


def test_resolve_flow_for_scope_with_scope():
    flow, source = resolve_flow_for_scope("home_services", "fontaneria")
    assert isinstance(flow, dict)
    assert source is not None


def test_resolve_flow_for_scope_missing_vertical():
    flow, source = resolve_flow_for_scope("missing_vertical", "default")
    assert flow == {}
    assert source is None
