import uuid

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_db
from app.core.config import get_settings
from app.main import app
from app.models.flows import Flow as FlowVersioned
from app.models.tenants import Tenant
from app.models.users import User
from app.services.config import tenant_prompt_config
from app.services.verticals import get_vertical_config, resolve_flow_id, vertical_prompt


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

    def commit(self):
        return None

    def rollback(self):
        return None

    def refresh(self, *args, **kwargs):
        return None

    def close(self):
        return None


@pytest.fixture
def client_with_tenant(monkeypatch):
    settings = get_settings()
    settings.jwt_secret = "demo-secret"
    settings.redis_url = "memory://"

    tenant_id = "tenant-demo"
    user = User(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        email="demo@example.com",
        hashed_password="stub",
        role="ADMIN",
        must_set_password=False,
        status="ACTIVE",
    )

    def _make(tenant_vertical_key: str | None):
        tenant = Tenant(
            id=tenant_id,
            customer_code="C0001",
            name="Demo",
            contact_email="demo@example.com",
            plan="BASE",
            idioma_default="es",
            timezone="Europe/Madrid",
            vertical_key=tenant_vertical_key,
        )
        db = _DB({User: [user], Tenant: [tenant], FlowVersioned: []})

        def override_get_db():
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        return TestClient(app), tenant_id

    yield _make

    app.dependency_overrides.clear()


def _login(client: TestClient, tenant_id: str) -> dict:
    resp = client.post(
        "/v1/auth/login",
        json={"email": "demo@example.com", "password": "secret"},
        headers={"X-Tenant-ID": tenant_id},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}", "X-Tenant-ID": tenant_id}


def test_kitchens_vertical_prompt_comes_from_file():
    text = vertical_prompt("kitchens")
    assert text
    assert "No cierres ventas" in text
    assert "cocinas" in text.lower()


def test_kitchens_vertical_config_merges_metadata():
    cfg = get_vertical_config("kitchens")
    assert cfg.get("label") == "Cocinas & Reformas"
    assert cfg.get("default_flow_id") == "kitchens_base_v1"
    assert isinstance(cfg.get("assets"), dict)


def test_resolve_flow_id_restricts_to_vertical_allowed():
    assert resolve_flow_id("kitchens_base_v1", "kitchens") == "kitchens_base_v1"
    assert resolve_flow_id("invalid_flow", "kitchens") == "kitchens_base_v1"


def test_tenant_prompt_config_appends_vertical_prompt_extension(monkeypatch):
    monkeypatch.setattr(tenant_prompt_config, "fetch_tenant_vertical_key", lambda tenant_id: "kitchens")
    cfg = tenant_prompt_config.get_tenant_prompt_config("tenant-demo")
    assert cfg.get("vertical_prompt")
    assert "No cierres ventas" in cfg["vertical_prompt"]
    assert "Nunca modifiques el flujo" in cfg["vertical_prompt"]


def test_flows_update_locked_for_vertical_tenant(client_with_tenant):
    client, tenant_id = client_with_tenant("kitchens")
    headers = _login(client, tenant_id)
    resp = client.post("/v1/flows/update", json={"blocks": {}}, headers=headers)
    assert resp.status_code == 403
    assert resp.json().get("detail") == "vertical_flow_locked"


def test_flows_update_allowed_for_legacy_tenant(client_with_tenant):
    client, tenant_id = client_with_tenant(None)
    headers = _login(client, tenant_id)
    resp = client.post("/v1/flows/update", json={"blocks": {}}, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("tenant_id") == tenant_id
    assert body.get("estado") == "published"
