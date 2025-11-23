import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import oauth2_scheme, require_auth
from app.api.deps import get_db
from app.models.flow import Flow, Scoring

router = APIRouter(prefix="/flows", tags=["flows"])
_FLOW_PATH = Path(__file__).resolve().parent.parent / "flows" / "base_flow.json"


def _load_flow() -> dict:
    with _FLOW_PATH.open() as f:
        return json.load(f)


def _save_flow(data: dict):
    with _FLOW_PATH.open("w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


@router.get("/{tenant_id}", dependencies=[Depends(require_auth)])
def get_flow(tenant_id: str, token: str = Depends(oauth2_scheme)):
    # Stub: lee el flujo base desde archivo ignorando tenant_id
    data = _load_flow()
    return {"tenant_id": tenant_id, "flow": data}


@router.get("/{tenant_id}/{version}", dependencies=[Depends(require_auth)])
def get_flow_version(tenant_id: str, version: str, token: str = Depends(oauth2_scheme)):
    data = _load_flow()
    return {"tenant_id": tenant_id, "version": version, "flow": data}


@router.post("/{tenant_id}", dependencies=[Depends(require_auth)])
def create_flow(tenant_id: str, payload: dict, token: str = Depends(oauth2_scheme)):
    # Stub: en futuro persistirá en DB; ahora eco del request.
    return {"tenant_id": tenant_id, "status": "received", "payload": payload}


@router.get("/current", dependencies=[Depends(require_auth)])
def get_current_flow(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    flow = db.query(Flow).filter(Flow.name == "base").first()
    if flow:
        return {"flow": flow.data}
    # fallback al json local si no hay registro en DB
    try:
        return {"flow": _load_flow()}
    except FileNotFoundError:
        return {"flow": {}}


@router.get("/scoring", dependencies=[Depends(require_auth)])
def get_scoring(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    scoring = db.query(Scoring).filter(Scoring.id == 1).first()
    if not scoring:
        scoring = Scoring(id=1, data={})
        db.add(scoring)
        db.commit()
        db.refresh(scoring)
    return scoring.data or {}


@router.post("/update", dependencies=[Depends(require_auth)])
def update_flow(payload: dict, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    if not payload:
        raise HTTPException(status_code=400, detail="invalid_payload")

    flow = db.query(Flow).filter(Flow.name == "base").first()
    if not flow:
        flow = Flow(name="base", data=payload)
        db.add(flow)
    else:
        flow.data = payload
    db.commit()
    db.refresh(flow)
    return flow.data
