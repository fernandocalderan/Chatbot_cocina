import os

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import or_

from app.api.auth import oauth2_scheme, require_auth
from app.api.deps import get_db, get_tenant_id
from app.models.leads import Lead
from app.services.pii_service import PIIService

router = APIRouter(prefix="/leads", tags=["leads"])
pii_service = PIIService()
PII_AUTO_UPGRADE = os.getenv("PII_AUTO_UPGRADE") == "1"


@router.get("/", dependencies=[Depends(require_auth)])
def list_leads(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=200),
    query: str | None = Query(default=None),
):
    q = db.query(Lead).filter(Lead.tenant_id == tenant_id)
    if query:
        like = f"%{query}%"
        q = q.filter(
            or_(
                Lead.meta_data["contact_name"].astext.ilike(like),
                Lead.meta_data["contact_email"].astext.ilike(like),
                Lead.meta_data["contact_phone"].astext.ilike(like),
            )
        )
    total = q.count()
    offset = (page - 1) * limit
    rows = q.order_by(Lead.created_at.desc()).offset(offset).limit(limit).all()

    def _meta_plain(lead_obj):
        meta = lead_obj.meta_data or {}
        # decrypt values if encrypted
        decrypted = pii_service.decrypt_meta(meta)
        if PII_AUTO_UPGRADE:
            enc_meta, changed = pii_service.encrypt_meta(decrypted, tenant_id)
            if changed:
                try:
                    lead_obj.meta_data = enc_meta
                    lead_obj.pii_version = 1
                    db.add(lead_obj)
                    db.commit()
                except Exception:
                    db.rollback()
        return decrypted

    items = [
        {
            "id": str(lead.id),
            "session_id": str(lead.session_id) if lead.session_id else None,
            "status": lead.status,
            "score": lead.score,
            "score_breakdown": lead.score_breakdown_json,
            "metadata": _meta_plain(lead),
            "created_at": lead.created_at.isoformat() if lead.created_at else None,
        }
        for lead in rows
    ]
    return {"items": items, "total": total, "page": page, "limit": limit}


@router.get("/{lead_id}", dependencies=[Depends(require_auth)])
def get_lead(
    lead_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    lead = (
        db.query(Lead).filter(Lead.id == lead_id, Lead.tenant_id == tenant_id).first()
    )
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="lead_not_found"
        )
    meta = pii_service.decrypt_meta(lead.meta_data or {})
    if PII_AUTO_UPGRADE:
        enc_meta, changed = pii_service.encrypt_meta(meta, tenant_id)
        if changed:
            try:
                lead.meta_data = enc_meta
                lead.pii_version = 1
                db.add(lead)
                db.commit()
            except Exception:
                db.rollback()
    return {
        "id": str(lead.id),
        "session_id": str(lead.session_id) if lead.session_id else None,
        "status": lead.status,
        "score": lead.score,
        "score_breakdown": lead.score_breakdown_json,
        "metadata": meta,
        "created_at": lead.created_at.isoformat() if lead.created_at else None,
    }
