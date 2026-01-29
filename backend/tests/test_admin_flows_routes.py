import os

# Ensure app uses dummy DB and accepts admin API key
os.environ.setdefault("DISABLE_DB", "1")
os.environ.setdefault("ADMIN_API_TOKEN", "test_admin_key")

from fastapi.testclient import TestClient

from app.main import app


def test_admin_import_and_publish_with_api_key():
    client = TestClient(app)
    file_content = (
        b'{"start_block":"welcome","blocks":{"welcome":{"type":"message","text":"hi","end":true}}}'
    )
    files = {"file": ("flow.json", file_content, "application/json")}
    data = {
        "vertical_key": "clinics_private",
        "scope_key": "smoke_scope",
        "flow_kind": "base",
        "owner_type": "GLOBAL",
    }
    headers = {"x-api-key": "test_admin_key"}
    resp = client.post("/v1/admin/flows/import", headers=headers, data=data, files=files)
    assert resp.status_code == 200
    flow_id = resp.json().get("flow_id")
    assert flow_id

    resp_pub = client.post(f"/v1/admin/flows/{flow_id}/publish", headers=headers)
    assert resp_pub.status_code == 200


def test_public_flow_import_moved():
    client = TestClient(app)
    resp = client.post("/v1/flows/import")
    assert resp.status_code == 410
