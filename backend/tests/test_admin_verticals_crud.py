import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import get_application


@pytest.fixture
def client(monkeypatch, tmp_path: Path):
    """
    Aísla los verticales en un tmp dir para no tocar `backend/app/verticals` real.
    """
    monkeypatch.setenv("DISABLE_DB", "1")

    # Patch vertical dirs (vertical_admin + verticals service)
    import app.services.vertical_admin as vadm
    import app.services.verticals as vsvc

    vroot = tmp_path / "verticals"
    vroot.mkdir(parents=True, exist_ok=True)
    (vroot / "registry.json").write_text("{}", encoding="utf-8")

    monkeypatch.setattr(vadm, "_VERTICALS_DIR", vroot, raising=True)
    monkeypatch.setattr(vadm, "_REGISTRY_PATH", vroot / "registry.json", raising=True)
    monkeypatch.setattr(vsvc, "_VERTICALS_DIR", vroot, raising=True)
    monkeypatch.setattr(vsvc, "_REGISTRY_PATH", vroot / "registry.json", raising=True)

    app = get_application()
    yield TestClient(app)


def test_admin_create_vertical_and_read_files(client: TestClient):
    resp = client.post(
        "/v1/admin/verticals",
        json={"key": "demo_vertical", "label": "Demo Vertical"},
        headers={"x-api-key": "any"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("key") == "demo_vertical"
    assert body.get("assets", {}).get("flow_base")

    read = client.get(
        "/v1/admin/verticals/demo_vertical/files/flow_base.json",
        headers={"x-api-key": "any"},
    )
    assert read.status_code == 200
    payload = read.json()
    assert payload.get("kind") == "json"
    assert isinstance(payload.get("content"), dict)
    assert payload["content"].get("start_block")


def test_admin_update_flow_base_validates(client: TestClient):
    client.post(
        "/v1/admin/verticals",
        json={"key": "demo_vertical", "label": "Demo Vertical"},
        headers={"x-api-key": "any"},
    )

    invalid_flow = {"start_block": "welcome", "blocks": {}}
    resp = client.put(
        "/v1/admin/verticals/demo_vertical/files/flow_base.json",
        json={"kind": "json", "content": invalid_flow, "validate": True},
        headers={"x-api-key": "any"},
    )
    assert resp.status_code == 400

    valid_flow = {
        "version": "demo_vertical_base_v1",
        "plan": "base",
        "start_block": "welcome",
        "languages": ["es"],
        "blocks": {
            "welcome": {"id": "welcome", "type": "message", "text": {"es": "Hola"}, "next": "end"},
            "end": {"id": "end", "type": "message", "text": {"es": "Fin"}, "next": None},
        },
    }
    resp2 = client.put(
        "/v1/admin/verticals/demo_vertical/files/flow_base.json",
        json={"kind": "json", "content": valid_flow, "validate": True},
        headers={"x-api-key": "any"},
    )
    assert resp2.status_code == 200
    body2 = resp2.json()
    assert body2.get("key") == "demo_vertical"

