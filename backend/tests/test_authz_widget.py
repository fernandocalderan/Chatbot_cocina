import datetime

import jwt
import pytest
from fastapi.testclient import TestClient

from app.main import get_application
from app.core.config import get_settings


def make_token(tenant_id: str, roles: list[str], token_type: str = "access"):
    settings = get_settings()
    exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    return jwt.encode(
        {
            "sub": "u1",
            "tenant_id": tenant_id,
            "roles": roles,
            "type": token_type,
            "exp": exp,
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("DISABLE_DB", "1")
    monkeypatch.setenv("PANEL_API_TOKEN", "devpaneltoken")
    monkeypatch.setenv("REDIS_URL", "memory://")
    get_settings.cache_clear()
    settings = get_settings()
    if not settings.jwt_secret:
        monkeypatch.setenv("JWT_SECRET", "testjwtsecret123")
        get_settings.cache_clear()
    yield


def test_require_role_denied():
    app = get_application()
    client = TestClient(app)
    token = make_token("t1", roles=["VIEWER"])
    res = client.post(
        "/v1/flows/update",
        json={"flow": "x"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 403


def test_require_role_allowed():
    app = get_application()
    client = TestClient(app)
    token = make_token("t1", roles=["ADMIN"])
    res = client.get("/v1/flows/current", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200


def test_widget_token_issue_and_use(monkeypatch):
    app = get_application()
    client = TestClient(app)
    token_admin = make_token("t1", roles=["ADMIN"])
    res_issue = client.post(
        "/v1/tenant/widget/token",
        json={"allowed_origin": "http://example.com", "ttl_minutes": 10},
        headers={"Authorization": f"Bearer {token_admin}", "X-Tenant-ID": "t1"},
    )
    assert res_issue.status_code == 200
    widget_token = res_issue.json()["token"]
    res_chat = client.post(
        "/v1/chat/send",
        json={"message": "hola"},
        headers={"Authorization": f"Bearer {widget_token}", "Idempotency-Key": "k1"},
    )
    assert res_chat.status_code == 200
