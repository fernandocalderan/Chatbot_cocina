from fastapi import APIRouter, Depends

from app.api.auth import oauth2_scheme, require_auth
from app.api.deps import get_db, get_tenant_id
from app.models.tenants import Tenant

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
