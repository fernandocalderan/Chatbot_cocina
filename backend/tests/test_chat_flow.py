import os

from fastapi.testclient import TestClient

from app.main import get_application
from app.core.config import get_settings


def test_chat_flow_initial_message():
    os.environ["DISABLE_DB"] = "1"
    os.environ["REDIS_URL"] = "memory://"
    os.environ["PANEL_API_TOKEN"] = "devpaneltoken"
    get_settings.cache_clear()
    client = TestClient(get_application())

    resp = client.post(
        "/v1/chat/send",
        json={"message": "hola", "session_id": "test-flow"},
        headers={"Idempotency-Key": "flow-1", "x-api-key": "devpaneltoken"},
    )
    assert resp.status_code == 200
    data = resp.json()

    assert data["session_id"] == "test-flow"
    assert data["block_id"]  # ensure we received a block id
    assert data["type"] in ("options", "message", "buttons")
    assert data.get("options") is not None
