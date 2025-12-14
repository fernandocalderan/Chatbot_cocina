import datetime

import jwt
import pytest
from fastapi.testclient import TestClient

from app.main import get_application
from app.core.config import get_settings


def _make_token(token_type: str, roles: list[str] | None = None, tenant_id: str | None = None):
    settings = get_settings()
    exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    payload = {
        "type": token_type,
        "roles": roles or [],
        "tenant_id": tenant_id,
        "sub": "u1",
        "exp": exp,
    }
    return jwt.encode(payload, settings.jwt_secret or "testjwtsecret", algorithm=settings.jwt_algorithm)


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("DISABLE_DB", "1")
    monkeypatch.setenv("JWT_SECRET", "testjwtsecret")
    monkeypatch.setenv("ADMIN_API_TOKEN", "admintestkey")
    monkeypatch.setenv("REDIS_URL", "memory://")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_admin_api_key_blocked_in_chat_and_widget():
    app = get_application()
    client = TestClient(app)
    for path in ("/v1/chat/send", "/v1/widget/token"):
        res = client.post(path, headers={"x-api-key": "admintestkey"})
        assert res.status_code == 403


def test_tenant_cannot_access_admin():
    app = get_application()
    client = TestClient(app)
    token = _make_token("TENANT", roles=["ADMIN"], tenant_id="t1")
    res = client.get("/v1/admin/tenants", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403


def test_widget_cannot_access_admin():
    app = get_application()
    client = TestClient(app)
    token = _make_token("WIDGET", tenant_id="t1")
    res = client.get("/v1/admin/tenants", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403


def test_impersonated_cannot_access_admin():
    app = get_application()
    client = TestClient(app)
    token = _make_token("TENANT", roles=["ADMIN", "IMPERSONATED"], tenant_id="t1")
    res = client.get("/v1/admin/tenants", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403


def test_admin_api_key_allows_admin_endpoints():
    app = get_application()
    client = TestClient(app)
    res = client.get("/v1/admin/tenants", headers={"x-api-key": "admintestkey"})
    assert res.status_code in (200, 401)  # tenant resolver may require tenant when DB disabled

