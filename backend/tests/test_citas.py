import os
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import get_application


def setup_module():
    os.environ["DISABLE_DB"] = "1"
    os.environ["REDIS_URL"] = "memory://"
    get_settings.cache_clear()


def test_appointments_book_requires_idempotency():
    client = TestClient(get_application())
    res = client.post("/v1/appointments/book", json={"slot": "2025-01-01T10:00:00Z"}, headers={"x-api-key": "devpaneltoken"})
    assert res.status_code == 400
    assert res.json()["detail"] == "missing_idempotency_key"


def test_appointments_book_idempotent_same_payload():
    client = TestClient(get_application())
    headers = {"Idempotency-Key": "appt-key", "x-api-key": "devpaneltoken"}
    payload = {"slot": "2025-01-01T10:00:00Z"}

    res1 = client.post("/v1/appointments/book", json=payload, headers=headers)
    res2 = client.post("/v1/appointments/book", json=payload, headers=headers)

    assert res1.status_code == 200
    assert res2.status_code == 200
    assert res1.json() == res2.json()


def test_appointments_book_conflict_on_different_payload():
    client = TestClient(get_application())
    headers = {"Idempotency-Key": "appt-key-conflict", "x-api-key": "devpaneltoken"}

    res1 = client.post("/v1/appointments/book", json={"slot": "2025-01-01T10:00:00Z"}, headers=headers)
    res2 = client.post("/v1/appointments/book", json={"slot": "2025-01-01T11:00:00Z"}, headers=headers)

    assert res1.status_code == 200
    assert res2.status_code == 409
    assert res2.json()["detail"] == "idempotency_conflict"
