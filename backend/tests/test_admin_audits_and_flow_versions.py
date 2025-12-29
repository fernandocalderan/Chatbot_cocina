import datetime
import uuid

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_db
from app.main import get_application
from app.models.audits import AuditLog
from app.models.flows import Flow as FlowVersioned
from app.models.tenants import Tenant


class _Query:
    def __init__(self, data):
        self._data = list(data)
        self._limit = None

    def _apply_condition(self, cond):
        left_key = getattr(getattr(cond, "left", None), "key", None)
        right = getattr(cond, "right", None)
        right_val = getattr(right, "value", right)
        if not left_key:
            return
        self._data = [row for row in self._data if getattr(row, left_key, None) == right_val]

    def filter(self, *conditions):
        for cond in conditions:
            self._apply_condition(cond)
        return self

    def order_by(self, *args, **kwargs):
        return self

    def limit(self, n: int):
        self._limit = n
        return self

    def first(self):
        return (self._data + [None])[0]

    def all(self):
        data = list(self._data)
        if self._limit is not None:
            data = data[: self._limit]
        return data


class _DB:
    def __init__(self, datasets):
        self._datasets = {k: list(v) for k, v in (datasets or {}).items()}

    def query(self, model):
        return _Query(self._datasets.get(model, []))

    def close(self):
        return None


@pytest.fixture
def admin_client_with_data(monkeypatch):
    monkeypatch.setenv("DISABLE_DB", "1")
    app = get_application()
    tenant_id = "tenant-demo"
    tenant = Tenant(
        id=tenant_id,
        customer_code="OPN-000001",
        name="Demo",
        contact_email="demo@example.com",
        plan="BASE",
        idioma_default="es",
        timezone="Europe/Madrid",
        vertical_key="kitchens",
    )

    now = datetime.datetime.now(datetime.timezone.utc)
    flows = [
        FlowVersioned(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            vertical_key="kitchens",
            version=1,
            schema_json={"blocks": {"a": {"type": "message"}}, "start_block": "a"},
            estado="published",
            published_at=now - datetime.timedelta(days=1),
            created_at=now - datetime.timedelta(days=1),
        ),
        FlowVersioned(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            vertical_key="kitchens",
            version=2,
            schema_json={"blocks": {"b": {"type": "message"}}, "start_block": "b"},
            estado="published",
            published_at=now,
            created_at=now,
        ),
    ]
    audits = [
        AuditLog(
            id=1,
            tenant_id=uuid.uuid4(),
            entity="tenant",
            entity_id=tenant_id,
            action="tenant.update",
            actor="admin_api_key",
            meta_data={"field": "plan"},
            created_at=now,
        )
    ]
    db = _DB({Tenant: [tenant], FlowVersioned: flows, AuditLog: audits})

    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client, tenant_id
    app.dependency_overrides.clear()


def test_admin_list_tenant_flow_versions(admin_client_with_data):
    client, tenant_id = admin_client_with_data
    resp = client.get(
        f"/v1/admin/tenants/{tenant_id}/flow/versions?limit=10&include_schema=true",
        headers={"x-api-key": "any"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("tenant_id") == tenant_id
    items = body.get("items") or []
    assert len(items) == 2
    assert {it.get("version") for it in items} == {1, 2}
    assert all("schema_json" in it for it in items)


def test_admin_audits_recent(admin_client_with_data):
    client, _tenant_id = admin_client_with_data
    resp = client.get("/v1/admin/audits/recent?limit=10", headers={"x-api-key": "any"})
    assert resp.status_code == 200
    body = resp.json()
    items = body.get("items") or []
    assert items
    assert items[0]["action"]
    assert items[0]["created_at"]
