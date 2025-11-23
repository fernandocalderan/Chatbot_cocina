from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_

from app.api.auth import oauth2_scheme, require_auth
from app.api.deps import get_db
from app.models.leads import Lead

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("/", dependencies=[Depends(require_auth)])
def list_leads(
    db=Depends(get_db),
    token: str = Depends(oauth2_scheme),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=200),
    query: str | None = Query(default=None),
):
    q = db.query(Lead)
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
    items = [
        {
            "id": str(lead.id),
            "session_id": str(lead.session_id) if lead.session_id else None,
            "status": lead.status,
            "score": lead.score,
            "score_breakdown": lead.score_breakdown_json,
            "metadata": lead.meta_data,
            "created_at": lead.created_at.isoformat() if lead.created_at else None,
        }
        for lead in rows
    ]
    return {"items": items, "total": total, "page": page, "limit": limit}


@router.get("/{lead_id}", dependencies=[Depends(require_auth)])
def get_lead(lead_id: str, db=Depends(get_db), token: str = Depends(oauth2_scheme)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return {}
    return {
        "id": str(lead.id),
        "session_id": str(lead.session_id) if lead.session_id else None,
        "status": lead.status,
        "score": lead.score,
        "score_breakdown": lead.score_breakdown_json,
        "metadata": lead.meta_data,
        "created_at": lead.created_at.isoformat() if lead.created_at else None,
    }
