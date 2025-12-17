from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import oauth2_scheme, require_auth
from app.middleware.authz import require_any_role
from app.api.deps import get_db, get_tenant_id
from app.models.flow import Scoring
from app.models.flows import Flow as FlowVersioned
from app.models.tenants import Tenant
from app.services.flow_templates import load_flow_template
from app.api.deps import DummySession

router = APIRouter(prefix="/flows", tags=["flows"])


@router.get("/current", dependencies=[Depends(require_auth)])
def get_current_flow(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme), current_tenant: str = Depends(get_tenant_id)
):
    if isinstance(db, DummySession):
        data = load_flow_template(None, plan_value="base")
        return {
            "tenant_id": current_tenant,
            "flow_id": None,
            "version": data.get("version") if isinstance(data, dict) else None,
            "estado": "fallback",
            "published_at": None,
            "flow": data if isinstance(data, dict) else {},
        }
    tenant = db.query(Tenant).filter(Tenant.id == current_tenant).first()
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
    # Para tenants con vertical, intentamos provisionar (idempotente) y volver a consultar.
    if tenant and getattr(tenant, "vertical_key", None):
        try:
            from app.services.verticals import provision_vertical_assets

            provision_vertical_assets(db, tenant)
        except Exception:
            pass
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

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="flow_not_provisioned")


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
    # Marcar flow activo si el modelo/DB lo soporta
    try:
        if tenant:
            tenant.active_flow_id = new_flow.id
            db.add(tenant)
    except Exception:
        pass
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
