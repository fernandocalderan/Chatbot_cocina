import os

os.environ.setdefault("DISABLE_DB", "1")
os.environ.setdefault("ADMIN_API_TOKEN", "test_admin_key")

from fastapi.testclient import TestClient

from app.main import app


def test_tenant_diff_requires_template():
    client = TestClient(app)
    headers = {"x-api-key": "test_admin_key"}
    resp = client.get(
        "/v1/tenants/tenant-1/diff",
        headers=headers,
        params={"vertical_key": "clinics_private", "scope_key": "scope", "flow_kind": "base"},
    )
    assert resp.status_code == 409


def test_tenant_sync_requires_template():
    client = TestClient(app)
    headers = {"x-api-key": "test_admin_key"}
    resp = client.post(
        "/v1/tenants/tenant-1/sync",
        headers=headers,
        json={"vertical_key": "clinics_private", "scope_key": "scope", "flow_kind": "base"},
    )
    assert resp.status_code == 409
