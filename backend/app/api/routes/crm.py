from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.auth import oauth2_scheme, require_auth
from app.api.deps import get_db, get_tenant_id
from app.models.activity import Activity
from app.models.leads import Lead
from app.models.task import Task
from app.services.crm_service import CRMService
from app.services.crm_metrics_service import CRMMetricsService

router = APIRouter(prefix="/crm", tags=["crm"])


def _parse_date(val: Optional[str]) -> Optional[datetime]:
    if not val:
        return None
    try:
        return datetime.fromisoformat(val)
    except ValueError:
        return None


@router.get("/leads/board", dependencies=[Depends(require_auth)])
def leads_board(db=Depends(get_db), tenant_id: str = Depends(get_tenant_id), token: str = Depends(oauth2_scheme)):
    statuses = ["nuevo", "contactado", "en_propuesta", "negociación", "ganado", "perdido"]
    result = {s: [] for s in statuses}
    leads = db.query(Lead).filter(Lead.tenant_id == tenant_id).all()
    for lead in leads:
        result.setdefault(lead.status, []).append({"id": str(lead.id), "status": lead.status, "owner_id": lead.owner_id})
    return result


@router.post("/leads/{lead_id}/move", dependencies=[Depends(require_auth)])
def move_lead(lead_id: str, payload: dict, db=Depends(get_db), tenant_id: str = Depends(get_tenant_id), token: str = Depends(oauth2_scheme)):
    new_status = payload.get("status")
    if not new_status:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="missing_status")
    service = CRMService(db)
    lead = service.move_lead_to_stage(lead_id, new_status, user=None, lost_reason=payload.get("lost_reason"))
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="lead_not_found")
    return {"id": str(lead.id), "status": lead.status}


@router.post("/leads/{lead_id}/assign", dependencies=[Depends(require_auth)])
def assign_lead(lead_id: str, payload: dict, db=Depends(get_db), tenant_id: str = Depends(get_tenant_id), token: str = Depends(oauth2_scheme)):
    owner_id = payload.get("owner_id")
    if not owner_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="missing_owner")
    service = CRMService(db)
    lead = service.assign_lead_owner(lead_id, owner_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="lead_not_found")
    return {"id": str(lead.id), "owner_id": str(owner_id)}


@router.get("/tasks", dependencies=[Depends(require_auth)])
def list_tasks(
    status: Optional[str] = Query(default=None),
    owner_id: Optional[str] = Query(default=None),
    lead_id: Optional[str] = Query(default=None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    q = db.query(Task).filter(Task.tenant_id == tenant_id)
    if status:
        q = q.filter(Task.status == status)
    if owner_id:
        q = q.filter(Task.owner_id == owner_id)
    if lead_id:
        q = q.filter(Task.lead_id == lead_id)
    items = q.order_by(Task.created_at.desc()).all()
    return [{"id": str(t.id), "title": t.title, "status": t.status} for t in items]


@router.post("/tasks", dependencies=[Depends(require_auth)])
def create_task(payload: dict, db=Depends(get_db), tenant_id: str = Depends(get_tenant_id), token: str = Depends(oauth2_scheme)):
    if not payload.get("title"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="missing_title")
    service = CRMService(db)
    task = service.create_task(tenant_id, payload)
    return {"id": str(task.id), "status": task.status}


@router.post("/tasks/{task_id}/complete", dependencies=[Depends(require_auth)])
def complete_task(task_id: str, db=Depends(get_db), tenant_id: str = Depends(get_tenant_id), token: str = Depends(oauth2_scheme)):
    service = CRMService(db)
    task = service.complete_task(task_id, user=None)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="task_not_found")
    return {"id": str(task.id), "status": task.status}


@router.get("/leads/{lead_id}/activities", dependencies=[Depends(require_auth)])
def lead_activities(lead_id: str, db=Depends(get_db), tenant_id: str = Depends(get_tenant_id), token: str = Depends(oauth2_scheme)):
    acts = (
        db.query(Activity)
        .filter(Activity.lead_id == lead_id, Activity.tenant_id == tenant_id)
        .order_by(Activity.created_at.desc())
        .all()
    )
    return [{"id": str(a.id), "type": a.type, "content": a.content, "created_at": a.created_at.isoformat()} for a in acts]


@router.get("/metrics/user/{user_id}", dependencies=[Depends(require_auth)])
def metrics_user(
    user_id: str,
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    svc = CRMMetricsService(db)
    return svc.get_user_performance(tenant_id, user_id, _parse_date(date_from), _parse_date(date_to))


@router.get("/metrics/funnel", dependencies=[Depends(require_auth)])
def metrics_funnel(
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    svc = CRMMetricsService(db)
    return svc.get_tenant_funnel(tenant_id, _parse_date(date_from), _parse_date(date_to))
