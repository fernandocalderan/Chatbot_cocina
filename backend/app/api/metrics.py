from fastapi import APIRouter, Depends

from app.api.auth import oauth2_scheme, require_auth
from app.api.deps import get_db, get_tenant_id
from app.models.tenants import Tenant
from app.middleware.authz import require_any_role
from app.services.ia_usage_service import IAUsageService

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/ai", dependencies=[Depends(require_auth)])
def ai_metrics(db=Depends(get_db), tenant_id: str = Depends(get_tenant_id), token: str = Depends(oauth2_scheme)):
    t = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not t:
        return {}
    return {
        "tenant_id": str(t.id),
        "ai_cost": t.ai_cost,
        "ai_monthly_limit": t.ai_monthly_limit,
    }


@router.get(
    "/ia/usage",
    dependencies=[Depends(require_any_role("OWNER", "ADMIN"))],
)
def ia_usage(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    usages = IAUsageService.get_monthly_usage(db, tenant_id)
    total_cost = IAUsageService.total_monthly_cost(db, tenant_id)
    return {
        "tenant_id": tenant_id,
        "entries": [
            {
                "date": str(u.date),
                "model": u.model,
                "tokens_in": u.tokens_in,
                "tokens_out": u.tokens_out,
                "cost_eur": float(u.cost_eur),
            }
            for u in usages
        ],
        "total_cost_eur": total_cost,
    }
