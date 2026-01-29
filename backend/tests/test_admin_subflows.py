import io
import os
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from fastapi import HTTPException
from starlette.datastructures import UploadFile

from app.api.v1.admin import subflows_admin
from app.models.flows import Flow as FlowVersioned

os.environ.setdefault("DISABLE_DB", "1")


class _FakeQuery:
    def __init__(self, data):
        self.data = list(data)

    def filter(self, *conditions):
        for cond in conditions:
            left_key = getattr(getattr(cond, "left", None), "key", None)
            if left_key is None:
                continue
            right = getattr(cond, "right", None)
            right_val = None
            if isinstance(right, sa.sql.elements.BindParameter):
                right_val = right.value
            elif right is None or isinstance(right, sa.sql.elements.Null):
                right_val = None
            else:
                right_val = getattr(right, "value", right)
            if isinstance(right_val, sa.sql.elements.ClauseElement):
                continue
            self.data = [row for row in self.data if getattr(row, left_key, None) == right_val]
        return self

    def update(self, values):
        for row in self.data:
            for key, val in values.items():
                setattr(row, key, val)
        return len(self.data)

    def first(self):
        return (self.data + [None])[0]

    def scalar(self):
        values = [getattr(row, "version", None) for row in self.data]
        values = [v for v in values if v is not None]
        return max(values) if values else None


class _FakeSession:
    def __init__(self, flows=None):
        self.flows = list(flows or [])

    def query(self, model):
        return _FakeQuery(self.flows)

    def add(self, obj):
        if getattr(obj, "id", None) is None:
            obj.id = "flow-test"
        self.flows.append(obj)
        return None

    def commit(self):
        return None

    def refresh(self, obj):
        return None


def _subflow_flow(flow_id: str, published: bool = False):
    return FlowVersioned(
        id=flow_id,
        flow_kind="subflow",
        parent_flow_id="base-1",
        subflow_key="lumbar",
        trigger_keywords=["lumbar"],
        trigger_priority=5,
        trigger_threshold=1,
        owner_type="GLOBAL",
        owner_id=None,
        estado="published" if published else "draft",
        published_at=datetime.now(timezone.utc) if published else None,
        archived=False,
        enabled=True,
        schema_json={"start_block": "welcome", "blocks": {"welcome": {"type": "message"}}},
        vertical_key="clinics_private",
        scope_key="osteopatia",
        version=1,
    )


def test_create_subflow_ok(monkeypatch):
    db = _FakeSession([])
    monkeypatch.setattr(subflows_admin, "_next_version_for_subflow", lambda *args, **kwargs: 1)
    payload = subflows_admin.SubflowCreatePayload(
        vertical_key="clinics_private",
        scope_key="osteopatia",
        parent_flow_id="base-1",
        subflow_key="dolor_lumbar",
        display_name="Dolor lumbar",
        content_text="Guia basica",
        trigger_keywords=["lumbar"],
        trigger_priority=7,
        trigger_threshold=1,
        owner_type="GLOBAL",
        owner_id=None,
    )
    res = subflows_admin.create_subflow(payload, db=db)
    assert res["status"] == "draft"
    assert res["version"] == 1


def test_import_subflow_ok(monkeypatch):
    db = _FakeSession([])
    monkeypatch.setattr(subflows_admin, "_next_version_for_subflow", lambda *args, **kwargs: 1)
    payload = {
        "start_block": "welcome",
        "blocks": {"welcome": {"type": "message", "text": "Hola"}},
    }
    file = UploadFile(filename="subflow.json", file=io.BytesIO(bytes(json_dump(payload), "utf-8")))
    res = subflows_admin.import_subflow(
        file=file,
        vertical_key="clinics_private",
        scope_key="osteopatia",
        parent_flow_id="base-1",
        subflow_key="dolor_lumbar",
        trigger_keywords="lumbar",
        trigger_priority=5,
        trigger_threshold=1,
        owner_type="GLOBAL",
        owner_id=None,
        db=db,
    )
    assert res["status"] == "draft"


def json_dump(payload):
    import json

    return json.dumps(payload)


def test_publish_subflow_unpublishes_previous():
    flow_old = _subflow_flow("flow-1", published=True)
    flow_new = _subflow_flow("flow-2", published=False)
    db = _FakeSession([flow_old, flow_new])

    res = subflows_admin.publish_subflow("flow-2", db=db)
    assert res["published"] is True
    assert flow_old.estado == "draft"
    assert flow_new.estado == "published"


def test_unique_subflow_key_enforced():
    existing = _subflow_flow("flow-1", published=False)
    db = _FakeSession([existing])
    payload = subflows_admin.SubflowCreatePayload(
        vertical_key="clinics_private",
        scope_key="osteopatia",
        parent_flow_id="base-1",
        subflow_key="lumbar",
        display_name="Lumbar",
        content_text="Texto",
        owner_type="GLOBAL",
        owner_id=None,
    )
    with pytest.raises(HTTPException) as exc:
        subflows_admin.create_subflow(payload, db=db)
    assert exc.value.status_code == 409


def test_update_subflow_toggle_enabled():
    flow = _subflow_flow("flow-1", published=False)
    db = _FakeSession([flow])
    payload = subflows_admin.SubflowUpdatePayload(enabled=False)
    res = subflows_admin.update_subflow("flow-1", payload, db=db)
    assert res["enabled"] is False
