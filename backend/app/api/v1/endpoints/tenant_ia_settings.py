from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.middleware.authz import require_any_role
from app.models.tenants import Tenant

router = APIRouter()


class IASettingsUpdate(BaseModel):
    ia_monthly_limit_eur: float = Field(
        ...,
        ge=1.0,
        le=10000.0,
        description="Nuevo límite mensual IA (EUR)",
    )


@router.patch(
    "/tenant/{tenant_id}/settings/ia",
    summary="Actualizar límite mensual IA de un tenant",
    tags=["tenant", "ia", "settings"],
)
def update_tenant_ia_settings(
    tenant_id: str,
    payload: IASettingsUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(require_any_role("OWNER", "ADMIN")),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    tenant.ia_monthly_limit_eur = payload.ia_monthly_limit_eur
    db.commit()
    db.refresh(tenant)

    return {
        "tenant_id": tenant_id,
        "ia_monthly_limit_eur": float(tenant.ia_monthly_limit_eur),
        "message": "Tenant IA monthly limit updated successfully.",
    }
