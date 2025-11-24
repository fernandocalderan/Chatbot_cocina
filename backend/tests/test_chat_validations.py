import os
from fastapi.testclient import TestClient

from app.core.session_manager import SessionManager
from app.core.config import get_settings
from app.main import get_application


def setup_module():
    os.environ["DISABLE_DB"] = "1"
    os.environ["REDIS_URL"] = "memory://"
    os.environ["PANEL_API_TOKEN"] = "devpaneltoken"
    get_settings.cache_clear()


def _client():
    return TestClient(get_application())


def test_phone_validation_reuses_session_state():
    client = _client()
    session_id = "test-phone-session"
    # Pre-cargar estado en Redis apuntando al bloque de teléfono
    settings = get_settings()
    mgr = SessionManager(settings.redis_url)
    mgr.save(session_id, {"current_block": "ask_contact_phone", "vars": {"tenant_id": "test-tenant"}})

    res = client.post(
        "/v1/chat/send",
        json={"message": "abc", "session_id": session_id},
        headers={"Idempotency-Key": "k-phone", "x-api-key": "devpaneltoken", "X-Tenant-ID": "test-tenant"},
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "invalid_phone"

    # Enviar un teléfono válido debe avanzar
    res_ok = client.post(
        "/v1/chat/send",
        json={"message": "+34123456789", "session_id": session_id},
        headers={"Idempotency-Key": "k-phone2", "x-api-key": "devpaneltoken", "X-Tenant-ID": "test-tenant"},
    )
    assert res_ok.status_code == 200
    data = res_ok.json()
    assert data["session_id"] == session_id
    assert data["state_summary"]["project_type"] is None or "project_type" in data["state_summary"]


def test_budget_validation_range():
    client = _client()
    session_id = "test-budget-session"
    settings = get_settings()
    mgr = SessionManager(settings.redis_url)
    mgr.save(session_id, {"current_block": "ask_budget", "vars": {"tenant_id": "test-tenant"}})

    res = client.post(
        "/v1/chat/send",
        json={"message": "100", "session_id": session_id},
        headers={"Idempotency-Key": "k-budget", "x-api-key": "devpaneltoken", "X-Tenant-ID": "test-tenant"},
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "invalid_budget"

    res_ok = client.post(
        "/v1/chat/send",
        json={"message": "1500-3000", "session_id": session_id},
        headers={"Idempotency-Key": "k-budget2", "x-api-key": "devpaneltoken", "X-Tenant-ID": "test-tenant"},
    )
    assert res_ok.status_code == 200
    assert res_ok.json()["session_id"] == session_id


def test_area_validation_range():
    client = _client()
    session_id = "test-area-session"
    settings = get_settings()
    mgr = SessionManager(settings.redis_url)
    mgr.save(session_id, {"current_block": "ask_measures", "vars": {"tenant_id": "test-tenant"}})

    res = client.post(
        "/v1/chat/send",
        json={"message": "0.1", "session_id": session_id},
        headers={"Idempotency-Key": "k-area", "x-api-key": "devpaneltoken", "X-Tenant-ID": "test-tenant"},
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "invalid_area"

    res_ok = client.post(
        "/v1/chat/send",
        json={"message": "3.2 x 2.4", "session_id": session_id},
        headers={"Idempotency-Key": "k-area2", "x-api-key": "devpaneltoken", "X-Tenant-ID": "test-tenant"},
    )
    assert res_ok.status_code == 200
    assert res_ok.json()["session_id"] == session_id
