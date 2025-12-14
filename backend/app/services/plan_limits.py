import os
from fastapi import Depends, HTTPException, status

from app.api.deps import get_db, get_tenant_id
from app.models.tenants import BillingStatus, Tenant
from app.services.ia_usage_service import IAUsageService
from app.services.pricing import get_plan_limits


def _load_tenant(db, tenant_id: str) -> Tenant:
    if os.getenv("DISABLE_DB") == "1":
        # Entorno de tests sin DB: devolver stub de tenant para no bloquear flujos
        class _Stub:
            id = tenant_id
            plan = "BASE"
            ia_enabled = True
            use_ia = True
            billing_status = BillingStatus.ACTIVE
        return _Stub()

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="tenant_not_found"
        )
    return tenant


def require_active_subscription(
    db=Depends(get_db), tenant_id: str = Depends(get_tenant_id)
):
    """
    Asegura que el tenant existe y tiene suscripción activa.
    Retorna un dict con tenant y límites para uso en handlers.
    """
    tenant = _load_tenant(db, tenant_id)
    limits = get_plan_limits(tenant.plan)
    billing_status = getattr(tenant, "billing_status", None)
    if billing_status and billing_status != BillingStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="subscription_inactive",
        )
    return {"tenant": tenant, "limits": limits}


def require_ia_access(
    db=Depends(get_db), tenant_id: str = Depends(get_tenant_id)
):
    """
    Verifica que el tenant puede usar IA:
    - Suscripción activa
    - IA habilitada en el plan
    - No excede coste mensual
    """
    ctx = require_active_subscription(db=db, tenant_id=tenant_id)
    tenant = ctx["tenant"]
    limits = ctx["limits"]
    ia_enabled = (limits.get("features") or {}).get("ia_enabled", True)
    if not ia_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="ia_not_in_plan"
        )
    if getattr(tenant, "ia_enabled", None) is False or getattr(tenant, "use_ia", None) is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="ia_disabled_for_tenant"
        )
    max_cost = limits.get("max_ia_cost")
    if max_cost is not None:
        spent = IAUsageService.total_monthly_cost(db, str(tenant.id))
        if spent >= max_cost:
            raise HTTPException(
                status.HTTP_402_PAYMENT_REQUIRED, detail="ia_quota_exceeded"
            )
    return ctx
