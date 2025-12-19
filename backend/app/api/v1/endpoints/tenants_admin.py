import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.middleware.authz import require_any_role
from app.models.tenants import Tenant
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
