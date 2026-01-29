import os
from datetime import datetime, timezone

from app.models.flows import Flow as FlowVersioned
from app.services import subflow_router
from conftest import DBStub

os.environ.setdefault("DISABLE_DB", "1")


def _flow(flow_id: str, owner_type: str = "GLOBAL", owner_id: str | None = None):
    return FlowVersioned(
        id=flow_id,
        flow_kind="subflow",
        parent_flow_id="base-1",
        subflow_key="dolor_lumbar",
        trigger_keywords=["lumbar"],
        trigger_priority=8,
        trigger_threshold=1,
        owner_type=owner_type,
        owner_id=owner_id,
        estado="published",
        published_at=datetime.now(timezone.utc),
        archived=False,
        enabled=True,
        schema_json={"start_block": "welcome", "blocks": {"welcome": {"type": "message"}}},
    )


def test_sticky_subflow_continue():
    flow = _flow("sf-1")
    db = DBStub({FlowVersioned: [flow]})

    res = subflow_router.pick_subflow(
        db=db,
        tenant_id=None,
        base_flow_id="base-1",
        user_text="cualquier texto",
        active_subflow_id="sf-1",
    )
    assert res["action"] == "keep_active"
    assert res["picked"].id == "sf-1"


def test_sticky_subflow_exit():
    flow = _flow("sf-1")
    db = DBStub({FlowVersioned: [flow]})

    res = subflow_router.pick_subflow(
        db=db,
        tenant_id=None,
        base_flow_id="base-1",
        user_text="volver al inicio",
        active_subflow_id="sf-1",
    )
    assert res["action"] == "exit"
    assert res["picked"] is None
