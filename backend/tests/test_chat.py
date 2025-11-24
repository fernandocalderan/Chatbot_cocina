import os

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app


def setup_module():
    # For tests, use in-memory session storage
    settings = get_settings()
    settings.redis_url = "memory://"
    settings.panel_api_token = "devpaneltoken"
    os.environ["DISABLE_DB"] = "1"


def test_chat_flow_advances_welcome_to_consent_and_to_ask_type():
    client = TestClient(app)

    # First message should move from welcome -> consent_gdpr
    res1 = client.post(
        "/v1/chat/send",
        json={"message": "hola", "lang": "es"},
        headers={"Idempotency-Key": "k1", "x-api-key": "devpaneltoken"},
    )
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["block_id"] == "consent_gdpr"
    assert "text" in data1

    # Second message with consent_yes should branch to ask_type
    res2 = client.post(
        "/v1/chat/send",
        json={"message": "consent_yes", "session_id": data1["session_id"]},
        headers={"Idempotency-Key": "k2", "x-api-key": "devpaneltoken"},
    )
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["block_id"] == "ask_type"
