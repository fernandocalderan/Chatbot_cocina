import os

from fastapi.testclient import TestClient

from app.main import get_application
from app.core.config import get_settings


def test_chat_flow_initial_message():
    os.environ["DISABLE_DB"] = "1"
    os.environ["REDIS_URL"] = "memory://"
    get_settings.cache_clear()
    client = TestClient(get_application())

    resp = client.post("/chat/send", json={"message": "hola", "session_id": "test-flow"})
    assert resp.status_code == 200
    data = resp.json()

    assert data["session_id"] == "test-flow"
    assert data["block_id"]  # ensure we received a block id
    assert data["type"] in ("options", "message")
    assert data.get("options") is not None
