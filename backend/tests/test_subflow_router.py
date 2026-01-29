import os
from datetime import datetime, timezone

import pytest

from app.models.flows import Flow as FlowVersioned
from app.services import subflow_router
from conftest import DBStub

os.environ.setdefault("DISABLE_DB", "1")


def _flow(
    *,
    flow_id: str,
    subflow_key: str,
    keywords: list[str],
    priority: int = 5,
    threshold: int = 1,
    owner_type: str = "GLOBAL",
    owner_id: str | None = None,
    parent_flow_id: str = "base-1",
):
    return FlowVersioned(
        id=flow_id,
        flow_kind="subflow",
        parent_flow_id=parent_flow_id,
        subflow_key=subflow_key,
        trigger_keywords=keywords,
        trigger_priority=priority,
        trigger_threshold=threshold,
        owner_type=owner_type,
        owner_id=owner_id,
        estado="published",
        published_at=datetime.now(timezone.utc),
        archived=False,
        schema_json={"start_block": "welcome", "blocks": {"welcome": {"type": "message"}}},
    )


def test_pick_subflow_by_priority(monkeypatch):
    flows = [
        _flow(flow_id="f1", subflow_key="lumbar", keywords=["lumbar"], priority=5),
        _flow(flow_id="f2", subflow_key="dolor_lumbar", keywords=["dolor", "lumbar"], priority=8),
    ]
    monkeypatch.setattr(
        subflow_router,
        "list_published_subflows",
        lambda *args, **kwargs: (flows, "GLOBAL"),
    )

    res = subflow_router.pick_subflow(
        db=None,
        tenant_id=None,
        base_flow_id="base-1",
        user_text="tengo dolor lumbar",
        active_subflow_id=None,
    )
    assert res["picked"] is not None
    assert res["picked"].id == "f2"


def test_pick_subflow_respects_threshold(monkeypatch):
    flows = [_flow(flow_id="f1", subflow_key="lumbar", keywords=["lumbar", "dolor"], threshold=2)]
    monkeypatch.setattr(
        subflow_router,
        "list_published_subflows",
        lambda *args, **kwargs: (flows, "GLOBAL"),
    )

    res = subflow_router.pick_subflow(
        db=None,
        tenant_id=None,
        base_flow_id="base-1",
        user_text="dolor",
        active_subflow_id=None,
    )
    assert res["picked"] is None


def test_pick_subflow_exit_keyword():
    res = subflow_router.pick_subflow(
        db=DBStub({}),
        tenant_id=None,
        base_flow_id="base-1",
        user_text="quiero volver al menu",
        active_subflow_id="f1",
    )
    assert res["action"] == "exit"
    assert res["picked"] is None


def test_list_published_subflows_prefers_tenant():
    tenant_flow = _flow(
        flow_id="t1",
        subflow_key="tenant_sf",
        keywords=["a"],
        owner_type="TENANT",
        owner_id="tenant-1",
    )
    global_flow = _flow(
        flow_id="g1",
        subflow_key="global_sf",
        keywords=["a"],
        owner_type="GLOBAL",
        owner_id=None,
    )
    db = DBStub({FlowVersioned: [tenant_flow, global_flow]})
    flows, source = subflow_router.list_published_subflows(db, tenant_id="tenant-1", base_flow_id="base-1")
    assert source == "TENANT"
    assert flows and flows[0].owner_type == "TENANT"
