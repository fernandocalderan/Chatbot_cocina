import datetime

import jwt
import pytest
from fastapi.testclient import TestClient

from app.main import get_application
from app.core.config import get_settings
from app.services.key_manager import KeyManager
from app.services.jwt_blacklist import JWTBlacklist


def make_token(secret, kid, jti, tenant_id="t1"):
    settings = get_settings()
    exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5)
    payload = {
        "sub": "u1",
        "tenant_id": tenant_id,
        "roles": ["ADMIN"],
        "type": "access",
        "exp": exp,
        "jti": jti,
    }
    return jwt.encode(
        payload, secret, algorithm=settings.jwt_algorithm, headers={"kid": kid}
    )


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("DISABLE_DB", "1")
    monkeypatch.setenv("REDIS_URL", "memory://")
    get_settings.cache_clear()
    yield


def test_token_with_current_key_valid(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "currentsecret123")
    get_settings.cache_clear()
    km = KeyManager()
    current_kid, current_secret, _ = km.get_jwt_keys()
    token = make_token(current_secret, current_kid, "j1")
    app = get_application()
    client = TestClient(app)
    res = client.get(
        "/v1/flows/current",
        headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": "t1"},
    )
    assert res.status_code in (200, 404)


def test_token_with_previous_key_valid(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "currentsecret123")
    monkeypatch.setenv("JWT_PRIVATE_KEY_PREVIOUS", "oldsecret")
    get_settings.cache_clear()
    token = make_token("oldsecret", "previous", "j2")
    app = get_application()
    client = TestClient(app)
    res = client.get(
        "/v1/flows/current",
        headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": "t1"},
    )
    assert res.status_code in (200, 404)


def test_blacklisted_token(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "currentsecret123")
    monkeypatch.setenv("REDIS_URL", "memory://")
    get_settings.cache_clear()
    km = KeyManager()
    current_kid, current_secret, _ = km.get_jwt_keys()
    token = make_token(current_secret, current_kid, "blocked")
    blacklist = JWTBlacklist(km.redis_url)
    blacklist.blacklist_token(
        "blocked", datetime.datetime.now(datetime.timezone.utc).timestamp() + 60
    )
    app = get_application()
    client = TestClient(app)
    res = client.get(
        "/v1/flows/current",
        headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": "t1"},
    )
    assert res.status_code == 401 or res.status_code == 403
