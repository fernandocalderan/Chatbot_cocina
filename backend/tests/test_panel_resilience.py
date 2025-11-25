from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.api.deps import get_db
from app.core.config import get_settings
from app.main import app
from conftest import DBStub


@pytest.fixture(autouse=True)
def _disable_db_env(monkeypatch):
    monkeypatch.setenv("DISABLE_DB", "1")
    yield
    monkeypatch.delenv("DISABLE_DB", raising=False)


@pytest.fixture
def force_password_ok(monkeypatch):
    import app.core.security
    import app.api.auth

    monkeypatch.setattr("app.core.security.verify_password", lambda plain, hashed: True)
    monkeypatch.setattr("app.api.auth.verify_password", lambda plain, hashed: True, raising=False)


@pytest.fixture
def dummy_db(monkeypatch):
    class FakeSession:
        def query(self, *args, **kwargs):
            return []

        def close(self):
            return None

    monkeypatch.setattr("app.middleware.tenant_resolver.SessionLocal", lambda: FakeSession())
    monkeypatch.setattr("app.api.deps.SessionLocal", lambda: FakeSession(), raising=False)
    yield


def _auth_headers(token: str, tenant_id: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "X-Tenant-ID": tenant_id}


def test_expired_token_returns_401(client_demo, demo_data, dummy_db):
    settings = get_settings()
    expired_token = jwt.encode(
        {"sub": demo_data["user"].id, "exp": datetime.now(timezone.utc) - timedelta(minutes=5)},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    resp = client_demo.get("/v1/leads", headers=_auth_headers(expired_token, demo_data["tenant_id"]))
    assert resp.status_code == 401


def test_invalid_token_returns_401(client_demo, demo_data, dummy_db):
    resp = client_demo.get("/v1/appointments", headers=_auth_headers("invalid.token", demo_data["tenant_id"]))
    assert resp.status_code == 401


def test_retry_after_transient_error(monkeypatch, demo_data, force_password_ok, dummy_db):
    settings = get_settings()
    if not settings.jwt_secret:
        settings.jwt_secret = "demo-secret"
    tenant_id = demo_data["tenant_id"]
    good_db = DBStub(
        {
            type(demo_data["user"]): [demo_data["user"]],
            type(demo_data["session"]): [demo_data["session"]],
            type(demo_data["leads"][0]): demo_data["leads"],
            type(demo_data["appointments"][0]): demo_data["appointments"],
            type(demo_data["flows"][0]): demo_data["flows"],
            type(demo_data["messages"][0]): demo_data["messages"],
        }
    )
    call_count = {"n": 0}

    def flaky_db():
        call_count["n"] += 1
        if call_count["n"] == 1:
            raise HTTPException(status_code=500, detail="db unavailable")
        try:
            yield good_db
        finally:
            good_db.close()

    app.dependency_overrides[get_db] = flaky_db
    client = TestClient(app)

    # login with good token
    token = jwt.encode(
        {"sub": demo_data["user"].id, "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    headers = _auth_headers(token, tenant_id)

    first = client.get("/v1/leads", headers=headers)
    assert first.status_code == 500

    second = client.get("/v1/leads", headers=headers)
    assert second.status_code == 200
    assert any(item["id"] == "lead-demo" for item in second.json()["items"])

    app.dependency_overrides.clear()
