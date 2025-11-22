from fastapi import APIRouter, Depends

from app.api.auth import require_auth
from app.api.deps import get_db
from app.models.tenants import Tenant

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/ai", dependencies=[Depends(require_auth)])
def ai_metrics(db=Depends(get_db)):
    rows = db.query(Tenant).all()
    return [
        {
            "tenant_id": str(t.id),
            "ai_cost": t.ai_cost,
            "ai_monthly_limit": t.ai_monthly_limit,
        }
        for t in rows
    ]
