import os

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import or_

from app.api.auth import oauth2_scheme, require_auth
from app.api.deps import get_db, get_tenant_id
from app.models.activity import Activity
from app.models.leads import Lead
from app.models.sessions import Session
from app.services.pii_service import PIIService
from app.middleware.authz import get_authz_context, AuthzContext

router = APIRouter(prefix="/leads", tags=["leads"])
pii_service = PIIService()
PII_AUTO_UPGRADE = os.getenv("PII_AUTO_UPGRADE") == "1"


def _assert_tenant_token(ctx: AuthzContext):
    if (ctx.token_type or "").upper() not in {"TENANT", "API_KEY"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="forbidden",
        )


@router.get("/", dependencies=[Depends(require_auth)])
def list_leads(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
    authz: AuthzContext = Depends(get_authz_context),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=200),
    status: str | None = Query(default=None),
    query: str | None = Query(default=None),
):
    _assert_tenant_token(authz)
    q = db.query(Lead).filter(Lead.tenant_id == tenant_id)
    if status:
        # Compat: panel usa "new" pero el modelo usa "nuevo" por defecto.
        status_norm = str(status).strip().lower()
        if status_norm in {"new", "nuevo"}:
            q = q.filter(Lead.status.in_(["new", "nuevo"]))
        else:
            q = q.filter(Lead.status == status_norm)
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

    session_ids = [r.session_id for r in rows if r.session_id]
    sessions_by_id: dict[str, dict] = {}
    if session_ids:
        sessions = db.query(Session).filter(Session.tenant_id == tenant_id, Session.id.in_(session_ids)).all()
        sessions_by_id = {str(s.id): (s.variables_json or {}) for s in sessions}

    lead_ids = [r.id for r in rows]
    last_activity_at: dict[str, str] = {}
    if lead_ids:
        acts = (
            db.query(Activity.lead_id, Activity.created_at)
            .filter(Activity.tenant_id == tenant_id, Activity.lead_id.in_(lead_ids))
            .order_by(Activity.lead_id.asc(), Activity.created_at.desc())
            .all()
        )
        for lead_id, created_at in acts:
            sid = str(lead_id)
            if sid in last_activity_at:
                continue
            last_activity_at[sid] = created_at.isoformat() if created_at else None

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
            "variables": sessions_by_id.get(str(lead.session_id)) if lead.session_id else None,
            "created_at": lead.created_at.isoformat() if lead.created_at else None,
            "updated_at": lead.updated_at.isoformat() if lead.updated_at else None,
            "last_activity_at": last_activity_at.get(str(lead.id)),
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
    authz: AuthzContext = Depends(get_authz_context),
):
    _assert_tenant_token(authz)
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
    variables = None
    if lead.session_id:
        sess = db.query(Session).filter(Session.tenant_id == tenant_id, Session.id == lead.session_id).first()
        variables = (sess.variables_json or {}) if sess else None
    return {
        "id": str(lead.id),
        "session_id": str(lead.session_id) if lead.session_id else None,
        "status": lead.status,
        "score": lead.score,
        "score_breakdown": lead.score_breakdown_json,
        "metadata": meta,
        "variables": variables,
        "created_at": lead.created_at.isoformat() if lead.created_at else None,
        "updated_at": lead.updated_at.isoformat() if lead.updated_at else None,
    }


class LeadPanelUpdate(BaseModel):
    internal_note: str | None = None
    quote_status: str | None = None  # pending|generated|sent


@router.patch("/{lead_id}/panel", dependencies=[Depends(require_auth)])
def update_lead_panel(
    lead_id: str,
    payload: LeadPanelUpdate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
    authz: AuthzContext = Depends(get_authz_context),
):
    _assert_tenant_token(authz)
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.tenant_id == tenant_id).first()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="lead_not_found")

    meta = dict(lead.meta_data or {})
    changed = False

    if payload.internal_note is not None:
        note = (payload.internal_note or "").strip()
        if note:
            meta["internal_note"] = note
        else:
            meta.pop("internal_note", None)
        changed = True

    if payload.quote_status is not None:
        status_norm = str(payload.quote_status).strip().lower()
        if status_norm in {"pendiente", "pending"}:
            meta["quote_status"] = "pending"
        elif status_norm in {"generado", "generated"}:
            meta["quote_status"] = "generated"
        elif status_norm in {"enviado", "sent"}:
            meta["quote_status"] = "sent"
            meta["quote_sent_at"] = datetime.now(timezone.utc).isoformat()
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_quote_status")
        changed = True

    if changed:
        lead.meta_data = meta
        db.add(lead)
        db.commit()

    return {"ok": True, "quote_status": meta.get("quote_status"), "has_internal_note": bool(meta.get("internal_note"))}
