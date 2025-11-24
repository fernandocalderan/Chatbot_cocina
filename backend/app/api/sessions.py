from fastapi import APIRouter, Depends, HTTPException

from app.api.auth import oauth2_scheme, require_auth
from app.api.deps import get_db, get_tenant_id
from app.models.sessions import Session
from app.models.messages import Message

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/{session_id}", dependencies=[Depends(require_auth)])
def get_session_state(session_id: str, db=Depends(get_db), tenant_id: str = Depends(get_tenant_id), token: str = Depends(oauth2_scheme)):
    session = db.query(Session).filter(Session.id == session_id, Session.tenant_id == tenant_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="session_not_found")

    msgs = (
        db.query(Message)
        .filter(Message.session_id == session_id, Message.tenant_id == tenant_id)
        .order_by(Message.id.asc())
        .all()
    )
    history = [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "block_id": m.block_id,
            "ai_meta": m.ai_meta or {},
            "attachments": m.attachments or [],
            "created_at": m.created_at.isoformat() if getattr(m, "created_at", None) else None,
        }
        for m in msgs
    ]

    return {
        "session_id": str(session.id),
        "tenant_id": str(session.tenant_id),
        "external_user_id": session.external_user_id,
        "canal": session.canal,
        "idioma_detectado": session.idioma_detectado,
        "state": session.state,
        "last_block_id": session.last_block_id,
        "variables": session.variables_json or {},
        "expires_at": session.expires_at.isoformat() if session.expires_at else None,
        "created_at": session.created_at.isoformat() if session.created_at else None,
        "updated_at": session.updated_at.isoformat() if session.updated_at else None,
        "history": history,
    }
