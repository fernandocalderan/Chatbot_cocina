import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_db
from app.main import get_application
from app.models.flows import Flow as FlowVersioned
from app.models.tenants import Tenant


class _Query:
    def __init__(self, data):
        self._data = list(data)

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

    def first(self):
        return (self._data + [None])[0]

    def all(self):
        return list(self._data)


class _DB:
    def __init__(self, datasets):
        self._datasets = {k: list(v) for k, v in (datasets or {}).items()}

    def query(self, model):
        return _Query(self._datasets.get(model, []))

    def add(self, obj):
        for model in self._datasets:
            if isinstance(obj, model):
                self._datasets[model].append(obj)
                return

    def flush(self):
        return None

    def commit(self):
        return None

    def rollback(self):
        return None

    def refresh(self, *args, **kwargs):
        return None

    def close(self):
        return None


@pytest.fixture
def admin_client(monkeypatch):
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
    db = _DB({Tenant: [tenant], FlowVersioned: []})

    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client, tenant_id
    app.dependency_overrides.clear()


def test_admin_get_tenant_flow_returns_fallback_from_vertical_files(admin_client):
    client, tenant_id = admin_client
    resp = client.get(f"/v1/admin/tenants/{tenant_id}/flow", headers={"x-api-key": "any"})
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("tenant_id") == tenant_id
    assert body.get("vertical_key") == "kitchens"
    assert isinstance(body.get("flow"), dict)
    assert isinstance(body["flow"].get("blocks"), dict)


def test_admin_publish_and_reset_tenant_flow(admin_client):
    client, tenant_id = admin_client

    publish_payload = {"blocks": {"welcome": {"type": "message"}}, "start_block": "welcome"}
    resp = client.post(
        f"/v1/admin/tenants/{tenant_id}/flow",
        json=publish_payload,
        headers={"x-api-key": "any"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("tenant_id") == tenant_id
    assert body.get("estado") == "published"
    assert body.get("version") == 1

    resp2 = client.post(
        f"/v1/admin/tenants/{tenant_id}/flow/reset",
        headers={"x-api-key": "any"},
    )
    assert resp2.status_code == 200
    body2 = resp2.json()
    assert body2.get("tenant_id") == tenant_id
    assert body2.get("estado") == "published"
    assert body2.get("version") == 2
