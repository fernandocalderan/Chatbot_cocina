from fastapi import APIRouter, Depends, HTTPException

from app.api.auth import require_auth
from app.api.deps import get_tenant_id
from app.services.billing_service import create_checkout_session

router = APIRouter(prefix="/billing", tags=["billing"])


@router.post("/checkout", dependencies=[Depends(require_auth)])
def start_checkout(price_id: str, tenant_id: str = Depends(get_tenant_id)):
    try:
        url = create_checkout_session(tenant_id, price_id)
        return {"checkout_url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
