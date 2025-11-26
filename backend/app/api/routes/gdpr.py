from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.auth import oauth2_scheme, require_auth
from app.api.deps import get_db, get_tenant_id
from app.services.gdpr_service import GDPRService

router = APIRouter(prefix="/gdpr", tags=["gdpr"])


@router.post("/forget", dependencies=[Depends(require_auth)])
def forget(
    payload: dict,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    lead_id = payload.get("lead_id")
    if not lead_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="missing_lead_id"
        )
    svc = GDPRService(db)
    ok = svc.forget_lead(tenant_id, lead_id, actor=None)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="lead_not_found"
        )
    return {"status": "ok"}


@router.post("/purge-tenant", dependencies=[Depends(require_auth)])
def purge_tenant(
    payload: dict,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    target_tenant = payload.get("tenant_id") or tenant_id
    svc = GDPRService(db)
    ok = svc.purge_tenant(target_tenant, actor=None)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="purge_failed"
        )
    return {"status": "ok"}


@router.get("/export", dependencies=[Depends(require_auth)])
def export_lead(
    lead_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    svc = GDPRService(db)
    data = svc.export_lead(tenant_id, lead_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="lead_not_found"
        )
    return data
