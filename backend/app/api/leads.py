from fastapi import APIRouter, Depends

from app.api.auth import require_panel_token
from app.api.deps import get_db
from app.models.leads import Lead

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("/", dependencies=[Depends(require_panel_token)])
def list_leads(db=Depends(get_db)):
    leads = db.query(Lead).all()
    return [
        {
            "id": str(lead.id),
            "session_id": str(lead.session_id) if lead.session_id else None,
            "status": lead.status,
            "score": lead.score,
            "score_breakdown": lead.score_breakdown_json,
            "metadata": lead.meta_data,
            "created_at": lead.created_at.isoformat() if lead.created_at else None,
        }
        for lead in leads
    ]
