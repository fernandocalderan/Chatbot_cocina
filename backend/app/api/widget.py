from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import get_settings
from app.core.session_manager import SessionManager
from app.models.leads import Lead as DBLead
from app.models.sessions import Session as DBSession
from app.models.tenants import Tenant
from app.services.agenda_service import AgendaService
from app.services.plan_limits import require_active_subscription
from app.services.flow_templates import load_flow_template, apply_materials
from app.services.verticals import resolve_flow_id
from app.models.configs import Config

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None


router = APIRouter(prefix="/widget", tags=["widget"])

WidgetState = Literal[
    "INICIADA",
    "EN_CONVERSACION",
    "LEAD_CREADO",
    "PRESUPUESTO_GENERADO",
    "CITA_SOLICITADA",
    "FINALIZADA",
]

def _safe_int(value, default: int) -> int:
    try:
        return int(float(value))
    except Exception:
        return default


def _require_widget(request: Request) -> str:
    token_type = (getattr(request.state, "token_type", None) or "").upper()
    tenant_id = getattr(request.state, "tenant_id", None)
    if token_type != "WIDGET" or not tenant_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing_widget_token")
    return str(tenant_id)


def _tenant_widget_config(db: Session, tenant: Tenant) -> dict:
    row = (
        db.query(Config)
        .filter(Config.tenant_id == tenant.id, Config.tipo == "tenant_widget_config")
        .order_by(Config.version.desc(), Config.updated_at.desc())
        .first()
    )
    visual = {}
    if row and isinstance(row.payload_json, dict):
        visual = row.payload_json.get("visual") if isinstance(row.payload_json.get("visual"), dict) else {}
    branding = getattr(tenant, "branding", {}) or {}
    widget_cfg = branding.get("widget") if isinstance(branding.get("widget"), dict) else {}

    primary_color = (
        visual.get("primary_color")
        or widget_cfg.get("primary_color")
        or branding.get("primary_color")
        or "#6B5B95"
    )
    secondary_color = visual.get("secondary_color") or "#EDE9FE"
    accent_color = visual.get("accent_color") or widget_cfg.get("accent_color") or "#C9A24D"
    position = visual.get("position") or widget_cfg.get("position") or "bottom-right"
    size = visual.get("size") or widget_cfg.get("size") or "md"
    tone = visual.get("tone") or widget_cfg.get("tone") or "serio"
    logo_url = visual.get("logo_url") or getattr(tenant, "logo_url", None)
    font_family = visual.get("font_family") or widget_cfg.get("font_family") or "Inter"
    font_size = visual.get("font_size") or widget_cfg.get("font_size") or 14
    border_radius = visual.get("border_radius") or widget_cfg.get("border_radius") or 16

    return {
        "tenant": {"id": str(tenant.id), "display_name": tenant.name or "Tu negocio"},
        "visual": {
            "primary_color": str(primary_color),
            "secondary_color": str(secondary_color),
            "accent_color": str(accent_color),
            "logo_url": logo_url,
            "position": str(position),
            "size": str(size),
            "tone": str(tone),
            "font_family": str(font_family),
            "font_size": _safe_int(font_size, 14),
            "border_radius": _safe_int(border_radius, 16),
        },
    }


def _load_materials(db: Session, tenant_id: str) -> dict | None:
    rows = (
        db.query(Config)
        .filter(Config.tenant_id == tenant_id, Config.tipo == "tenant_flow_materials")
        .order_by(Config.version.desc(), Config.updated_at.desc())
        .all()
    )
    for row in rows:
        payload = row.payload_json or {}
        if str(payload.get("status") or "").upper() == "PUBLISHED":
            return payload
    return None


def _runtime_messages(flow_data: dict, materials: dict | None) -> dict:
    content = materials.get("content") if isinstance(materials, dict) else {}
    welcome = content.get("welcome") if isinstance(content, dict) else None
    errors = content.get("errors") if isinstance(content, dict) else {}
    closing = content.get("closing") if isinstance(content, dict) else None
    language = content.get("language") if isinstance(content, dict) else None
    tone = content.get("tone") if isinstance(content, dict) else None
    start_id = flow_data.get("start_block") if isinstance(flow_data, dict) else None
    blocks = flow_data.get("blocks") if isinstance(flow_data.get("blocks"), dict) else {}
    if not welcome and start_id and start_id in blocks:
        welcome = blocks[start_id].get("text")
    if not closing and "end" in blocks:
        closing = blocks["end"].get("text")
    return {
        "welcome": welcome or "Hola. ¿En qué puedo ayudarte?",
        "errors": errors or {"offline": "Nuestro asistente no está disponible."},
        "closing": closing or "",
        "language": language or "es",
        "tone": tone or "serio",
    }


def _get_widget_runtime(db: Session, tenant: Tenant) -> dict:
    materials = _load_materials(db, str(tenant.id))
    flow_id = materials.get("flow_id") if isinstance(materials, dict) else None
    flow_id = resolve_flow_id(flow_id, getattr(tenant, "vertical_key", None))
    plan_value = getattr(tenant, "plan", "base")
    if hasattr(plan_value, "value"):
        plan_value = plan_value.value
    flow_data = load_flow_template(flow_id, plan_value=str(plan_value or "base").lower())
    flow_data = apply_materials(flow_data, materials)

    visual_payload = _tenant_widget_config(db, tenant)
    automation = materials.get("automation") if isinstance(materials, dict) else {}
    messages = _runtime_messages(flow_data, materials)
    visual = visual_payload.get("visual") or {}
    tokens = {
        "colors": {
            "primary": visual.get("primary_color"),
            "secondary": visual.get("secondary_color"),
            "accent": visual.get("accent_color"),
        },
        "font": {
            "family": visual.get("font_family"),
            "size_base": visual.get("font_size"),
        },
        "bubble": {
            "position": visual.get("position"),
            "size": visual.get("size"),
            "border_radius": visual.get("border_radius"),
        },
        "tone": visual.get("tone") or messages.get("tone"),
    }
    runtime = {
        "visual": visual,
        "tokens": tokens,
        "messages": messages,
        "automation": automation or {"ai_level": "medium", "saving_mode": False, "human_fallback": True},
        "flow_id": flow_id or flow_data.get("version") or "default",
        "tenant": visual_payload.get("tenant"),
    }
    return runtime


def _compute_state(
    *,
    current: WidgetState,
    ended: bool,
    has_lead: bool,
    is_appointment_step: bool,
) -> WidgetState:
    if ended:
        return "FINALIZADA"
    if is_appointment_step:
        return "CITA_SOLICITADA"
    if has_lead:
        return "LEAD_CREADO"
    if current == "INICIADA":
        return "EN_CONVERSACION"
    return current


def _merge_session_vars(db_state: DBSession, extra: dict) -> None:
    vars_ = db_state.variables_json or {}
    if not isinstance(vars_, dict):
        vars_ = {}
    for k, v in extra.items():
        if v is not None:
            vars_[k] = v
    db_state.variables_json = vars_


class WidgetSessionCreate(BaseModel):
    tenant_id: str = Field(..., description="Tenant ID (debe coincidir con el token)")


@router.get("/config")
def get_widget_config(request: Request, db: Session = Depends(get_db)):
    tenant_id = _require_widget(request)
    require_active_subscription(db=db, tenant_id=tenant_id)
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tenant_not_found")
    runtime = _get_widget_runtime(db, tenant)
    return {
        "tenant": runtime.get("tenant"),
        "visual": runtime.get("visual"),
        "conversation": {
            "welcome_message": runtime.get("messages", {}).get("welcome"),
            "language": (runtime.get("messages", {}) or {}).get("language", "es"),
            "flow_id": runtime.get("flow_id"),
        },
        "automation": runtime.get("automation"),
    }


@router.get("/runtime")
def get_widget_runtime(request: Request, db: Session = Depends(get_db)):
    tenant_id = _require_widget(request)
    require_active_subscription(db=db, tenant_id=tenant_id)
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tenant_not_found")
    return _get_widget_runtime(db, tenant)


@router.post("/session")
def create_widget_session(payload: WidgetSessionCreate, request: Request, db: Session = Depends(get_db)):
    tenant_id = _require_widget(request)
    require_active_subscription(db=db, tenant_id=tenant_id)
    if str(payload.tenant_id) != str(tenant_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="tenant_mismatch")

    # Crear sesión backend-driven (id del backend, persistente).
    sess = DBSession(tenant_id=tenant_id, canal="web_widget", state=None, variables_json={})
    db.add(sess)
    db.commit()
    db.refresh(sess)

    _merge_session_vars(
        sess,
        {
            "tenant_id": str(tenant_id),
            "channel": "web_widget",
            "widget_state": "INICIADA",
            "lead_id": None,
        },
    )
    db.add(sess)
    db.commit()

    settings = get_settings()
    SessionManager(settings.redis_url).save(str(sess.id), {"vars": dict(sess.variables_json or {})})

    return {"session_id": str(sess.id), "state": "INICIADA"}


class WidgetMessagePayload(BaseModel):
    value: str


class WidgetMessageInput(BaseModel):
    session_id: str
    type: Literal["text", "button", "selection"]
    payload: WidgetMessagePayload


def _chat_send_as_widget(
    *,
    tenant_id: str,
    session_id: str,
    message: str,
    language: str | None,
    db: Session,
) -> dict:
    # Llama a la lógica existente (FlowEngine) sin exponer /chat al widget.
    from app.api.chat import ChatInput, send_message

    idempotency_key = f"widget-{session_id}-{int(datetime.now(timezone.utc).timestamp())}"
    return send_message(
        payload=ChatInput(message=message, session_id=session_id, lang=language),
        idempotency_key=idempotency_key,
        tenant_id=tenant_id,
        db=db,
        token="",
    )


def _widget_response_from_chat(
    *,
    chat_resp: dict,
    widget_state: WidgetState,
) -> dict:
    messages: list[dict] = []
    text = chat_resp.get("message") or chat_resp.get("ai_reply") or chat_resp.get("text") or ""
    if text:
        messages.append({"type": "text", "content": str(text)})
    opts = chat_resp.get("options") or []
    if isinstance(opts, list) and opts:
        labels = []
        for o in opts:
            if isinstance(o, dict):
                labels.append(str(o.get("label") or o.get("id") or ""))
            else:
                labels.append(str(o))
        labels = [x for x in labels if x]
        if labels:
            messages.append({"type": "buttons", "options": labels})
    return {"messages": messages, "state": widget_state}


@router.post("/message")
def widget_message(payload: WidgetMessageInput, request: Request, db: Session = Depends(get_db)):
    tenant_id = _require_widget(request)
    require_active_subscription(db=db, tenant_id=tenant_id)

    sess = db.query(DBSession).filter(DBSession.id == payload.session_id).first()
    if not sess or str(sess.tenant_id) != str(tenant_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="session_not_found")

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tenant_not_found")
    materials = _load_materials(db, str(tenant_id)) or {}
    content_cfg = materials.get("content") if isinstance(materials.get("content"), dict) else {}
    lang = content_cfg.get("language") or "es"

    value = (payload.payload.value or "").strip()
    if not value:
        raise HTTPException(status_code=400, detail="empty_message")

    chat_resp = _chat_send_as_widget(
        tenant_id=str(tenant_id),
        session_id=str(payload.session_id),
        message=value,
        language=str(lang) if lang else None,
        db=db,
    ) or {}

    # Compute canonical widget state
    lead = (
        db.query(DBLead)
        .filter(DBLead.session_id == payload.session_id, DBLead.tenant_id == tenant_id)
        .first()
    )
    lead_id = str(lead.id) if lead else None
    ended = bool((SessionManager(get_settings().redis_url).load(str(payload.session_id)) or {}).get("ended"))
    is_appointment_step = (chat_resp.get("type") or "") in {"appointment", "calendar"}
    current_state = (sess.variables_json or {}).get("widget_state") or "INICIADA"
    next_state: WidgetState = _compute_state(
        current=str(current_state),
        ended=ended,
        has_lead=bool(lead_id),
        is_appointment_step=is_appointment_step,
    )

    _merge_session_vars(sess, {"widget_state": next_state, "lead_id": lead_id, "language": lang})
    db.add(sess)
    db.commit()

    # Persist also to Redis state vars so future chat steps keep it.
    settings = get_settings()
    mgr = SessionManager(settings.redis_url)
    st_state = mgr.load(str(payload.session_id)) or {}
    vars_ = st_state.get("vars") if isinstance(st_state.get("vars"), dict) else {}
    vars_["widget_state"] = next_state
    if lead_id:
        vars_["lead_id"] = lead_id
    vars_["channel"] = "web_widget"
    if lang:
        vars_["language"] = lang
    st_state["vars"] = vars_
    mgr.save(str(payload.session_id), st_state)

    out = _widget_response_from_chat(chat_resp=chat_resp, widget_state=next_state)
    if lead_id:
        out["lead_id"] = lead_id
    return out


@router.get("/agenda/slots")
def widget_agenda_slots(session_id: str, request: Request, db: Session = Depends(get_db)):
    tenant_id = _require_widget(request)
    require_active_subscription(db=db, tenant_id=tenant_id)

    sess = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not sess or str(sess.tenant_id) != str(tenant_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="session_not_found")

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    tz_name = getattr(tenant, "timezone", None) or "UTC"
    tzinfo = ZoneInfo(tz_name) if ZoneInfo else timezone.utc
    slot_minutes = int(getattr(tenant, "slot_duration", None) or 30)

    slots = AgendaService(db=db).get_slots(str(tenant_id), visit_type=None, location=None, db=db) or []
    out = []
    for s in slots[:50]:
        try:
            start_utc = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
            end_utc = start_utc + timedelta(minutes=slot_minutes)
            start_local = start_utc.astimezone(tzinfo)
            end_local = end_utc.astimezone(tzinfo)
            out.append(
                {
                    "start": start_local.strftime("%Y-%m-%dT%H:%M"),
                    "end": end_local.strftime("%Y-%m-%dT%H:%M"),
                }
            )
        except Exception:
            continue
    return {"slots": out}


class WidgetAgendaConfirm(BaseModel):
    session_id: str
    slot_start: str


@router.post("/agenda/confirm")
def widget_agenda_confirm(payload: WidgetAgendaConfirm, request: Request, db: Session = Depends(get_db)):
    tenant_id = _require_widget(request)
    require_active_subscription(db=db, tenant_id=tenant_id)

    sess = db.query(DBSession).filter(DBSession.id == payload.session_id).first()
    if not sess or str(sess.tenant_id) != str(tenant_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="session_not_found")

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    tz_name = getattr(tenant, "timezone", None) or "UTC"
    tzinfo = ZoneInfo(tz_name) if ZoneInfo else timezone.utc
    try:
        naive = datetime.fromisoformat(payload.slot_start)
        local = naive.replace(tzinfo=tzinfo)
        slot_iso = local.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    except Exception:
        raise HTTPException(status_code=400, detail="invalid_slot")

    materials = _load_materials(db, str(tenant_id)) or {}
    content_cfg = materials.get("content") if isinstance(materials.get("content"), dict) else {}
    lang = content_cfg.get("language") or "es"
    chat_resp = _chat_send_as_widget(
        tenant_id=str(tenant_id),
        session_id=str(payload.session_id),
        message=slot_iso,
        language=str(lang) if lang else None,
        db=db,
    ) or {}

    lead = (
        db.query(DBLead)
        .filter(DBLead.session_id == payload.session_id, DBLead.tenant_id == tenant_id)
        .first()
    )
    lead_id = str(lead.id) if lead else None
    ended = bool((SessionManager(get_settings().redis_url).load(str(payload.session_id)) or {}).get("ended"))
    next_state: WidgetState = _compute_state(
        current=str((sess.variables_json or {}).get("widget_state") or "EN_CONVERSACION"),
        ended=ended,
        has_lead=bool(lead_id),
        is_appointment_step=False,
    )
    _merge_session_vars(sess, {"widget_state": next_state, "lead_id": lead_id, "language": lang})
    db.add(sess)
    db.commit()

    settings = get_settings()
    mgr = SessionManager(settings.redis_url)
    st_state = mgr.load(str(payload.session_id)) or {}
    vars_ = st_state.get("vars") if isinstance(st_state.get("vars"), dict) else {}
    vars_["widget_state"] = next_state
    if lead_id:
        vars_["lead_id"] = lead_id
    vars_["channel"] = "web_widget"
    if lang:
        vars_["language"] = lang
    st_state["vars"] = vars_
    mgr.save(str(payload.session_id), st_state)

    out = _widget_response_from_chat(chat_resp=chat_resp, widget_state=next_state)
    if lead_id:
        out["lead_id"] = lead_id
    return out
