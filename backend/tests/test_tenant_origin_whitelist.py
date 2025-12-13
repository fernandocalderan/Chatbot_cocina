from datetime import datetime, timedelta, timezone

import jwt
from fastapi.testclient import TestClient

from app.api.deps import get_db
from app.core.config import get_settings
from app.main import app
from app.middleware import tenant_resolver
from app.models.tenants import Tenant
from app.models.users import User


class StubQuery:
    def __init__(self, obj):
        self.obj = obj

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self.obj


class StubSession:
    def __init__(self, mapping):
        self.mapping = mapping

    def query(self, model):
        return StubQuery(self.mapping.get(model))

    def close(self):
        return None


def test_origin_whitelist_allows_and_blocks(monkeypatch):
    monkeypatch.setenv("DISABLE_DB", "0")
    settings = get_settings()
    settings.jwt_secret = "origin-secret"
    allowed_origin = "https://allowed.example.com"
    blocked_origin = "https://evil.example.com"

    tenant = Tenant(
        id="tenant-origin",
        name="Tenant Origin",
        contact_email="t@example.com",
            plan="PRO",
        branding={"allowed_origins": [allowed_origin]},
        idioma_default="es",
        timezone="Europe/Madrid",
    )
    user = User(id="user-origin", tenant_id=tenant.id, email="u@example.com", hashed_password="stub")

    stub_session = StubSession({Tenant: tenant, User: user})
    monkeypatch.setattr(tenant_resolver, "SessionLocal", lambda: stub_session)
    # Override get_db to avoid real DB connection
    def override_get_db():
        try:
            yield stub_session
        finally:
            stub_session.close()

    app.dependency_overrides[get_db] = override_get_db

    token = jwt.encode(
        {"sub": str(user.id), "exp": datetime.now(timezone.utc) + timedelta(minutes=10)},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    headers_allowed = {"Authorization": f"Bearer {token}", "Origin": allowed_origin}
    headers_blocked = {"Authorization": f"Bearer {token}", "Origin": blocked_origin}

    client = TestClient(app)

    ok_resp = client.get("/v1/tenant/config", headers=headers_allowed)
    assert ok_resp.status_code == 200
    assert ok_resp.json()["tenant_id"] == str(tenant.id)

    bad_resp = client.get("/v1/tenant/config", headers=headers_blocked)
    assert bad_resp.status_code == 401
    assert bad_resp.json().get("detail") == "origin_not_allowed"

    app.dependency_overrides.clear()
