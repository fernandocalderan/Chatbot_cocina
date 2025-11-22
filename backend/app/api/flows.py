import json
from pathlib import Path

from fastapi import APIRouter, Depends

from app.api.auth import require_panel_token

router = APIRouter(prefix="/flows", tags=["flows"])


@router.get("/{tenant_id}", dependencies=[Depends(require_panel_token)])
def get_flow(tenant_id: str):
    # Stub: lee el flujo base desde archivo ignorando tenant_id
    flow_path = Path(__file__).resolve().parent.parent / "flows" / "base_flow.json"
    with flow_path.open() as f:
        data = json.load(f)
    return {"tenant_id": tenant_id, "flow": data}


@router.get("/{tenant_id}/{version}", dependencies=[Depends(require_panel_token)])
def get_flow_version(tenant_id: str, version: str):
    flow_path = Path(__file__).resolve().parent.parent / "flows" / "base_flow.json"
    with flow_path.open() as f:
        data = json.load(f)
    return {"tenant_id": tenant_id, "version": version, "flow": data}


@router.post("/{tenant_id}", dependencies=[Depends(require_panel_token)])
def create_flow(tenant_id: str, payload: dict):
    # Stub: en futuro persistirá en DB; ahora eco del request.
    return {"tenant_id": tenant_id, "status": "received", "payload": payload}
