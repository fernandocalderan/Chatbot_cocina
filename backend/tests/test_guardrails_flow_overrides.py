import os
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.admin_flows import publish_flow_by_id
from app.api.deps import get_db
from app.main import app
from app.models.flows import Flow as FlowVersioned
from app.models.tenants import Tenant
from app.services import flow_resolver
from conftest import DBStub

os.environ.setdefault("DISABLE_DB", "1")
os.environ.setdefault("ADMIN_API_TOKEN", "test_admin_key")


def test_resolve_runtime_flow_logging_does_not_crash(monkeypatch):
    tenant = SimpleNamespace(id="tenant-1", vertical_key="clinics_private", branding={}, plan="base")
    resolved = flow_resolver.ResolvedFlow(
        id="flow-1",
        version=1,
        estado="published",
        published_at=None,
        schema_json={"start_block": "welcome", "blocks": {"welcome": {"type": "message"}}},
        source="TENANT_OVERRIDE",
    )
    monkeypatch.setattr(flow_resolver, "resolve_active_flow", lambda *args, **kwargs: resolved)

    result = flow_resolver.resolve_runtime_flow(
        db=None,
        tenant=tenant,
        flow_id_override=None,
        plan_value="base",
    )
    assert isinstance(result, dict)


class _FakeQuery:
    def __init__(self, data):
        self.data = list(data)

    def filter(self, *conditions):
        for cond in conditions:
            left_key = getattr(getattr(cond, "left", None), "key", None)
            if left_key is None:
                continue
            right = getattr(cond, "right", None)
            right_val = getattr(right, "value", right)
            self.data = [row for row in self.data if getattr(row, left_key, None) == right_val]
        return self

    def update(self, values):
        for row in self.data:
            for key, val in values.items():
                setattr(row, key, val)
        return len(self.data)

    def first(self):
        return (self.data + [None])[0]


class _FakeSession:
    def __init__(self, flows):
        self._flows = flows

    def query(self, model):
        if model is FlowVersioned:
            return _FakeQuery(self._flows)
        return _FakeQuery([])

    def add(self, *args, **kwargs):
        return None

    def commit(self):
        return None

    def refresh(self, *args, **kwargs):
        return None


def test_publish_enforces_single_published_per_group():
    flow_1 = SimpleNamespace(
        id="flow-1",
        owner_type="GLOBAL",
        owner_id=None,
        vertical_key="clinics_private",
        scope_key="osteopatia",
        flow_kind="base",
        estado="draft",
        published_at=None,
        version=1,
    )
    flow_2 = SimpleNamespace(
        id="flow-2",
        owner_type="GLOBAL",
        owner_id=None,
        vertical_key="clinics_private",
        scope_key="osteopatia",
        flow_kind="base",
        estado="draft",
        published_at=None,
        version=2,
    )
    db = _FakeSession([flow_1, flow_2])

    publish_flow_by_id(flow_1.id, db=db)
    publish_flow_by_id(flow_2.id, db=db)

    published = [flow for flow in (flow_1, flow_2) if flow.estado == "published"]
    assert len(published) == 1
    assert published[0].id == flow_2.id


def test_tenant_actions_require_vertical_key():
    tenant = Tenant(id="tenant-1", name="Demo", customer_code="demo", vertical_key=None)
    db_stub = DBStub({Tenant: [tenant]})

    def override_get_db():
        try:
            yield db_stub
        finally:
            db_stub.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    headers = {"x-api-key": "test_admin_key"}

    try:
        resp = client.get(
            "/v1/tenants/tenant-1/diff",
            headers=headers,
            params={"vertical_key": "clinics_private", "scope_key": "scope", "flow_kind": "base"},
        )
        assert resp.status_code == 409
        assert resp.json()["detail"]["error"] == "tenant_missing_vertical_key"

        resp = client.post(
            "/v1/tenants/tenant-1/sync",
            headers=headers,
            json={"vertical_key": "clinics_private", "scope_key": "scope", "flow_kind": "base"},
        )
        assert resp.status_code == 409
        assert resp.json()["detail"]["error"] == "tenant_missing_vertical_key"

        resp = client.post(
            "/v1/tenants/tenant-1/publish",
            headers=headers,
            json={
                "vertical_key": "clinics_private",
                "scope_key": "scope",
                "flow_kind": "base",
                "published": True,
            },
        )
        assert resp.status_code == 409
        assert resp.json()["detail"]["error"] == "tenant_missing_vertical_key"
    finally:
        app.dependency_overrides.clear()
