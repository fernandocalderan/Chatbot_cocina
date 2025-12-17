import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import oauth2_scheme, require_auth
from app.middleware.authz import require_any_role
from app.api.deps import get_db, get_tenant_id
from app.models.flow import Scoring
from app.models.flows import Flow as FlowVersioned
from app.models.tenants import Tenant

router = APIRouter(prefix="/flows", tags=["flows"])
_FLOW_PATH = Path(__file__).resolve().parent.parent / "flows" / "lead_intake_v1.json"


def _load_flow() -> dict:
    with _FLOW_PATH.open() as f:
        return json.load(f)


@router.get("/current", dependencies=[Depends(require_auth)])
def get_current_flow(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme), current_tenant: str = Depends(get_tenant_id)
):
    # Buscar la versión publicada más reciente para el tenant
    flow = (
        db.query(FlowVersioned)
        .filter(FlowVersioned.tenant_id == current_tenant, FlowVersioned.estado == "published")
        .order_by(FlowVersioned.published_at.desc().nullslast(), FlowVersioned.version.desc())
        .first()
    )
    if flow:
        return {
            "tenant_id": current_tenant,
            "flow_id": str(flow.id),
            "version": flow.version,
            "estado": flow.estado,
            "published_at": flow.published_at.isoformat() if flow.published_at else None,
            "flow": flow.schema_json,
        }
    # fallback al json local (lead_intake_v1) si no hay registro en DB
    try:
        data = _load_flow()
        return {
            "tenant_id": current_tenant,
            "flow_id": None,
            "version": data.get("version"),
            "estado": "fallback",
            "published_at": None,
            "flow": data,
        }
    except FileNotFoundError:
        return {"tenant_id": current_tenant, "flow": {}}


@router.get("/scoring", dependencies=[Depends(require_auth)])
def get_scoring(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme), current_tenant: str = Depends(get_tenant_id)
):
    scoring = db.query(Scoring).filter(Scoring.id == 1).first()
    if not scoring:
        scoring = Scoring(id=1, data={})
        db.add(scoring)
        db.commit()
        db.refresh(scoring)
    return scoring.data or {}


@router.post("/update", dependencies=[Depends(require_any_role("OWNER", "ADMIN"))])
def update_flow(
    payload: dict,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    current_tenant: str = Depends(get_tenant_id),
):
    if not payload:
        raise HTTPException(status_code=400, detail="invalid_payload")

    tenant = db.query(Tenant).filter(Tenant.id == current_tenant).first()
    if tenant and getattr(tenant, "vertical_key", None):
        raise HTTPException(status_code=403, detail="vertical_flow_locked")

    latest_flow = (
        db.query(FlowVersioned)
        .filter(FlowVersioned.tenant_id == current_tenant)
        .order_by(FlowVersioned.version.desc())
        .first()
    )
    next_version = (latest_flow.version + 1) if latest_flow else 1

    new_flow = FlowVersioned(
        tenant_id=current_tenant,
        version=next_version,
        schema_json=payload,
        estado="published",
        published_at=datetime.now(timezone.utc),
    )
    db.add(new_flow)
    db.commit()
    db.refresh(new_flow)
    return {
        "tenant_id": current_tenant,
        "flow_id": str(new_flow.id),
        "version": new_flow.version,
        "estado": new_flow.estado,
        "published_at": new_flow.published_at.isoformat() if new_flow.published_at else None,
        "flow": new_flow.schema_json,
    }
