from fastapi import APIRouter, HTTPException

from app.services.billing_service import create_checkout_session

router = APIRouter(prefix="/billing", tags=["billing"])


@router.post("/checkout")
def start_checkout(tenant_id: str, price_id: str):
    try:
        url = create_checkout_session(tenant_id, price_id)
        return {"checkout_url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
