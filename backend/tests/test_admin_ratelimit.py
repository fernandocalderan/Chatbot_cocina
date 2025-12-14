import datetime

import jwt
import pytest
from fastapi.testclient import TestClient

from app.main import get_application
from app.core.config import get_settings


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("DISABLE_DB", "1")
    monkeypatch.setenv("JWT_SECRET", "testjwtsecret")
    monkeypatch.setenv("ADMIN_API_TOKEN", "admintestkey")
    monkeypatch.setenv("REDIS_URL", "memory://")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _make_admin_token():
    settings = get_settings()
    exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    return jwt.encode(
        {"type": "ADMIN", "roles": ["SUPER_ADMIN"], "exp": exp},
        settings.jwt_secret or "testjwtsecret",
        algorithm=settings.jwt_algorithm,
    )


def test_admin_rate_limit(monkeypatch):
    app = get_application()
    client = TestClient(app)
    # Simula un contador en memoria para validar que el guard se ejecuta
    counter = {"n": 0}

    def fake_check(redis_url: str, key: str, limit_per_min: int) -> bool:
        counter["n"] += 1
        return counter["n"] <= limit_per_min

    monkeypatch.setattr("app.middleware.rate_limiter.check_rate_limit", fake_check, raising=False)

    token = _make_admin_token()
    for _ in range(35):
        res = client.get("/v1/admin/tenants", headers={"Authorization": f"Bearer {token}"})
        if res.status_code == 429:
            assert counter["n"] > 30
            return
    assert False, "Expected 429 after exceeding rate limit"
