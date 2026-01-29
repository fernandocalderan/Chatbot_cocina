import uuid
from typing import Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.middleware.authz import require_any_role
from app.models.flows import Flow as FlowVersioned
from app.models.tenant_flow_overrides import TenantFlowOverride
from app.models.tenants import Tenant
from app.services.flow_diff import diff_json
from app.services.template_service import TemplateService
from app.services.verticals import get_vertical_config, provision_vertical_assets

router = APIRouter(prefix="/tenants", tags=["tenants"])


class TenantCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    contact_email: Optional[str] = Field(None, max_length=320)
    contact_phone: Optional[str] = Field(None, max_length=64)
    address_street: Optional[str] = Field(None, max_length=255)
    address_number: Optional[str] = Field(None, max_length=64)
    address_postal_code: Optional[str] = Field(None, max_length=32)
    address_city: Optional[str] = Field(None, max_length=128)
    plan: Optional[str] = Field("BASE", description="Plan inicial BASE/PRO/ELITE")
    timezone: Optional[str] = Field("Europe/Madrid", max_length=64)
    idioma_default: Optional[str] = Field("es", max_length=10)
    vertical_key: Optional[str] = Field(None, max_length=64)


class TenantFlowSyncPayload(BaseModel):
    vertical_key: str = Field(..., min_length=1)
    scope_key: str = Field(..., min_length=1)
    flow_kind: str = Field("base", min_length=1)


class TenantFlowPublishPayload(BaseModel):
    vertical_key: str = Field(..., min_length=1)
    scope_key: str = Field(..., min_length=1)
    flow_kind: str = Field("base", min_length=1)
    published: bool = True


def _latest_published_template(
    db: Session, *, vertical_key: str, scope_key: str, flow_kind: str
) -> FlowVersioned | None:
    try:
        return (
            db.query(FlowVersioned)
            .filter(
                FlowVersioned.owner_type == "GLOBAL",
                FlowVersioned.owner_id.is_(None),
                FlowVersioned.estado == "published",
                FlowVersioned.vertical_key == vertical_key,
                FlowVersioned.scope_key == scope_key,
                FlowVersioned.flow_kind == flow_kind,
            )
            .order_by(FlowVersioned.published_at.desc().nullslast(), FlowVersioned.version.desc())
            .first()
        )
    except Exception:
        return None


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_any_role("SUPER_ADMIN"))],
    summary="Crear un nuevo tenant (solo superadmin)",
)
def create_tenant(payload: TenantCreate, db: Session = Depends(get_db)):
    tenant_id = uuid.uuid4()
    if not payload.vertical_key:
        raise HTTPException(status_code=400, detail="missing_vertical_key")
    if not get_vertical_config(payload.vertical_key):
        raise HTTPException(status_code=400, detail="invalid_vertical_key")

    # Evitar duplicados por nombre
    exists = db.query(Tenant).filter(Tenant.name == payload.name).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="tenant_name_exists"
        )

    branding = {}
    phone = (payload.contact_phone or "").strip() or None
    if phone:
        branding["contact_phone"] = phone
    address = {
        "street": (payload.address_street or "").strip() or None,
        "number": (payload.address_number or "").strip() or None,
        "postal_code": (payload.address_postal_code or "").strip() or None,
        "city": (payload.address_city or "").strip() or None,
    }
    address = {k: v for k, v in address.items() if v}
    if address:
        branding["address"] = address

    tenant = Tenant(
        id=tenant_id,
        name=payload.name,
        contact_email=payload.contact_email,
        plan=payload.plan or "BASE",
        timezone=payload.timezone or "Europe/Madrid",
        idioma_default=payload.idioma_default or "es",
        vertical_key=payload.vertical_key,
        branding=branding,
        flow_mode="VERTICAL",
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    try:
        cloned_tpl = TemplateService.clone_default_template(db, str(tenant.id))
        if cloned_tpl:
            tenant.default_template_id = cloned_tpl.id
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
    except Exception:
        db.rollback()
    try:
        provision_vertical_assets(db, tenant)
    except Exception:
        db.rollback()

    return {
        "id": str(tenant.id),
        "name": tenant.name,
        "plan": tenant.plan,
        "contact_email": tenant.contact_email,
        "timezone": tenant.timezone,
        "idioma_default": tenant.idioma_default,
        "default_template_id": str(getattr(tenant, "default_template_id")) if getattr(tenant, "default_template_id", None) else None,
        "vertical_key": tenant.vertical_key,
    }


@router.get(
    "/{tenant_id}/diff",
    dependencies=[Depends(require_any_role("SUPER_ADMIN"))],
    summary="Diff entre template publicado y override del tenant",
)
def diff_tenant_flow(
    tenant_id: str,
    vertical_key: str,
    scope_key: str,
    flow_kind: str = "base",
    db: Session = Depends(get_db),
):
    base = _latest_published_template(db, vertical_key=vertical_key, scope_key=scope_key, flow_kind=flow_kind)
    if not base or not isinstance(base.schema_json, dict):
        raise HTTPException(status_code=409, detail="template_not_found")

    override = (
        db.query(TenantFlowOverride)
        .filter(TenantFlowOverride.tenant_id == tenant_id, TenantFlowOverride.base_flow_id == base.id)
        .first()
    )
    override_json = override.draft_json if override and isinstance(override.draft_json, dict) else {}
    diff = diff_json(base.schema_json or {}, override_json or {})
    return {
        "tenant_id": tenant_id,
        "base_flow_id": str(base.id),
        "base_version": base.version,
        "override_flow_id": str(override.flow_id) if override else None,
        "override_published": bool(getattr(override, "published", False)),
        "override_published_at": override.published_at.isoformat() if override and override.published_at else None,
        "override_updated_at": override.updated_at.isoformat() if override and override.updated_at else None,
        "diff": diff,
    }


@router.post(
    "/{tenant_id}/sync",
    dependencies=[Depends(require_any_role("SUPER_ADMIN"))],
    summary="Sincronizar tenant con template publicado (crea/actualiza override draft)",
)
def sync_tenant_flow(
    tenant_id: str,
    payload: TenantFlowSyncPayload,
    db: Session = Depends(get_db),
):
    base = _latest_published_template(
        db, vertical_key=payload.vertical_key, scope_key=payload.scope_key, flow_kind=payload.flow_kind
    )
    if not base or not isinstance(base.schema_json, dict):
        raise HTTPException(status_code=409, detail="template_not_found")

    override = (
        db.query(TenantFlowOverride)
        .filter(TenantFlowOverride.tenant_id == tenant_id, TenantFlowOverride.base_flow_id == base.id)
        .first()
    )
    if not override:
        override = TenantFlowOverride(
            tenant_id=tenant_id,
            base_flow_id=base.id,
            draft_json=base.schema_json,
            published=False,
            published_at=None,
        )
        db.add(override)
    else:
        override.draft_json = base.schema_json
        override.published = False
        override.published_at = None
        db.add(override)
    db.commit()
    db.refresh(override)
    return {
        "tenant_id": tenant_id,
        "base_flow_id": str(base.id),
        "override_flow_id": str(override.flow_id),
        "published": bool(override.published),
        "updated_at": override.updated_at.isoformat() if override.updated_at else None,
    }


@router.post(
    "/{tenant_id}/publish",
    dependencies=[Depends(require_any_role("SUPER_ADMIN"))],
    summary="Publicar/Despublicar override del tenant",
)
def publish_tenant_override(
    tenant_id: str,
    payload: TenantFlowPublishPayload,
    db: Session = Depends(get_db),
):
    base = _latest_published_template(
        db, vertical_key=payload.vertical_key, scope_key=payload.scope_key, flow_kind=payload.flow_kind
    )
    if not base:
        raise HTTPException(status_code=409, detail="template_not_found")

    override = (
        db.query(TenantFlowOverride)
        .filter(TenantFlowOverride.tenant_id == tenant_id, TenantFlowOverride.base_flow_id == base.id)
        .first()
    )
    if not override:
        raise HTTPException(status_code=404, detail="override_not_found")

    if payload.published:
        override.published = True
        override.published_at = datetime.now(timezone.utc)
    else:
        override.published = False
        override.published_at = None
    db.add(override)
    db.commit()
    db.refresh(override)
    return {
        "tenant_id": tenant_id,
        "override_flow_id": str(override.flow_id),
        "published": bool(override.published),
        "published_at": override.published_at.isoformat() if override.published_at else None,
    }
