from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import oauth2_scheme, require_auth
from app.middleware.authz import require_any_role
from app.api.deps import get_db, get_tenant_id
from app.models.configs import Config
from app.models.flow import Scoring
from app.models.flows import Flow as FlowVersioned
from app.models.tenants import Tenant
from app.services.flow_resolver import resolve_active_flow, FlowResolutionError
from app.api.deps import DummySession

router = APIRouter(prefix="/flows", tags=["flows"])

CONFIG_TIPO_MATERIALS = "tenant_flow_materials"


def _primary_scope(tenant: Tenant | None) -> str | None:
    if not tenant:
        return None
    branding = getattr(tenant, "branding", {}) or {}
    scopes = branding.get("vertical_scopes") or []
    if isinstance(scopes, list) and scopes:
        return str(scopes[0])
    return None


def _load_latest_published_flow(db: Session, tenant_id: str) -> dict | None:
    try:
        flow = (
            db.query(FlowVersioned)
            .filter(FlowVersioned.tenant_id == tenant_id, FlowVersioned.estado == "published")
            .order_by(FlowVersioned.published_at.desc().nullslast(), FlowVersioned.version.desc())
            .first()
        )
    except Exception:
        return None
    if not flow or not isinstance(getattr(flow, "schema_json", None), dict):
        return None
    return {
        "tenant_id": tenant_id,
        "flow_id": str(flow.id),
        "version": flow.version,
        "estado": flow.estado,
        "published_at": flow.published_at.isoformat() if flow.published_at else None,
        "flow": flow.schema_json,
    }


def _load_published_materials(db: Session, tenant_id: str) -> dict | None:
    try:
        rows = (
            db.query(Config)
            .filter(Config.tenant_id == tenant_id, Config.tipo == CONFIG_TIPO_MATERIALS)
            .order_by(Config.version.desc(), Config.updated_at.desc())
            .all()
        )
    except Exception:
        return None
    for row in rows:
        payload = row.payload_json or {}
        if str(payload.get("status") or "").upper() == "PUBLISHED":
            return payload if isinstance(payload, dict) else None
    return None


@router.get("/current", dependencies=[Depends(require_auth)])
def get_current_flow(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme), current_tenant: str = Depends(get_tenant_id)
):
    if isinstance(db, DummySession):
        raise HTTPException(status_code=409, detail="no_published_flow")

    tenant = db.query(Tenant).filter(Tenant.id == current_tenant).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="tenant_not_found")

    try:
        row = resolve_active_flow(db, str(tenant.id))
    except FlowResolutionError as exc:
        raise HTTPException(status_code=409, detail=exc.code)
    if not isinstance(getattr(row, "schema_json", None), dict):
        raise HTTPException(status_code=409, detail="invalid_published_flow")
    return {
        "tenant_id": current_tenant,
        "flow_id": str(row.id),
        "version": row.version,
        "estado": row.estado,
        "published_at": row.published_at.isoformat() if row.published_at else None,
        "flow": row.schema_json,
    }


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

    # Unpublish any previous published flow for this tenant
    db.query(FlowVersioned).filter(
        FlowVersioned.tenant_id == current_tenant, FlowVersioned.estado == "published"
    ).update({"estado": "draft", "published_at": None})

    new_flow = FlowVersioned(
        tenant_id=current_tenant,
        version=next_version,
        schema_json=payload,
        estado="published",
        published_at=datetime.now(timezone.utc),
    )
    try:
        tenant_scope = _primary_scope(tenant)
        new_flow.scope_key = tenant_scope
        new_flow.owner_type = "TENANT"
        new_flow.owner_id = tenant.id if tenant else None
        new_flow.flow_kind = "base"
    except Exception:
        pass
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


@router.post("/import")
def import_flow_base_stub():
    raise HTTPException(status_code=410, detail="moved_to_admin: /v1/admin/flows/import")


@router.post("/{flow_id}/publish")
def publish_flow_stub(flow_id: str):
    raise HTTPException(
        status_code=410,
        detail=f"moved_to_admin: /v1/admin/flows/{flow_id}/publish",
    )
