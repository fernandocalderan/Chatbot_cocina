import json
import re
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.auth import require_panel_token
from app.api.deps import get_db
from app.core.config import get_settings
from app.core.flow_engine import FlowEngine
from app.core.session_manager import SessionManager
from app.core.intent_classifier import IntentClassifier
from app.core.actions import ActionExecutor
from app.models.sessions import Session as DBSesion
from app.models.leads import Lead as DBLead
from app.models.messages import Message as DBMessage
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatInput(BaseModel):
    message: str
    session_id: Optional[str] = None
    lang: Optional[str] = None


def load_base_flow() -> dict:
    flow_dir = Path(__file__).resolve().parent.parent / "flows"
    primary = flow_dir / "lead_intake_v1.json"
    fallback = flow_dir / "base_flow.json"
    flow_path = primary if primary.exists() else fallback
    with flow_path.open() as f:
        return json.load(f)


def validate_input(block: dict, user_input: str):
    validation = block.get("validation")
    if not validation:
        return
    vtype = validation.get("type")
    if vtype == "text_length":
        min_chars = validation.get("min_chars", 0)
        max_chars = validation.get("max_chars", 10_000)
        if not (min_chars <= len(user_input) <= max_chars):
            raise HTTPException(status_code=400, detail="invalid_length")
    elif vtype == "phone":
        if not re.match(r"^\+?\d{7,15}$", user_input):
            raise HTTPException(status_code=400, detail="invalid_phone")
    elif vtype == "email_optional":
        if user_input.strip() == "":
            return
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", user_input):
            raise HTTPException(status_code=400, detail="invalid_email")


def pick_lang(flow: dict, requested: Optional[str]) -> str:
    langs = flow.get("languages") or []
    if requested and requested in langs:
        return requested
    if langs:
        return langs[0]
    return "es"


def save_message(db, session_id: str, tenant_id, role: str, content: str, block_id: Optional[str] = None, ai_meta=None):
    try:
        msg = DBMessage(
            tenant_id=tenant_id,
            session_id=session_id,
            role=role,
            content=content,
            block_id=block_id,
            ai_meta=ai_meta or {},
            attachments=[],
        )
        db.add(msg)
        db.commit()
    except SQLAlchemyError:
        db.rollback()


def compute_score(vars_data: dict, scoring_cfg: dict) -> tuple[int, dict]:
    weights = scoring_cfg.get("weights", {})
    breakdown = {}
    total_weight = sum(weights.values()) or 1

    def add(field: str, raw_score: int):
        w = weights.get(field, 0)
        breakdown[field] = {"score": raw_score, "weight": w}
        return raw_score * w

    budget_score = 70 if vars_data.get("budget") else 0
    urgency_value = vars_data.get("urgency")
    urgency_map = scoring_cfg.get("mappings", {}).get("urgency", {}).get("es", {})
    urgency_score = urgency_map.get(urgency_value, 50 if urgency_value else 0)

    measures_score = 60 if vars_data.get("measures") else 0
    style_score = 80 if vars_data.get("style") else 0
    origin_score = 50 if vars_data.get("origin") else 0

    weighted_sum = 0
    weighted_sum += add("budget", budget_score)
    weighted_sum += add("urgency", urgency_score)
    weighted_sum += add("area_m2", measures_score)
    weighted_sum += add("style_defined", style_score)
    weighted_sum += add("origin", origin_score)

    score = round(weighted_sum / total_weight) if total_weight else 0
    return score, breakdown


def map_score_to_status(score: int, thresholds: dict) -> str:
    if score >= thresholds.get("premium_min", 90):
        return "premium"
    if score >= thresholds.get("hot_min", 70):
        return "hot"
    if score >= thresholds.get("warm_min", 40):
        return "warm"
    return "cold"


@router.get("/history/{session_id}")
def get_history(session_id: str, db=Depends(get_db)):
    msgs = (
        db.query(DBMessage)
        .filter(DBMessage.session_id == session_id)
        .order_by(DBMessage.id.asc())
        .all()
    )
    return [
        {"role": m.role, "content": m.content, "block_id": m.block_id, "created_at": m.created_at.isoformat() if m.created_at else None}
        for m in msgs
    ]


@router.post("/send", dependencies=[Depends(require_panel_token)])
def send_message(payload: ChatInput, db=Depends(get_db)):  # db kept for future use
    settings = get_settings()
    session_mgr = SessionManager(settings.redis_url)
    flow_data = load_base_flow()
    engine = FlowEngine(flow_data)
    intent = IntentClassifier()
    executor = ActionExecutor(settings)

    session_id = payload.session_id or ""
    state = session_mgr.load(session_id) if session_id else {}
    if not session_id:
        import uuid

        session_id = str(uuid.uuid4())
        state = {"current_block": flow_data.get("start_block", "start"), "vars": {}}
        session_mgr.save(session_id, state)
        try:
            db_obj = DBSesion(
                id=session_id,
                tenant_id=None,
                canal="web",
                state=state.get("current_block"),
                variables_json=state.get("vars", {}),
            )
            db.add(db_obj)
            db.commit()
        except SQLAlchemyError:
            db.rollback()

    start_block = flow_data.get("start_block", "start")
    current_block_id = state.get("current_block", start_block)
    current_block = engine.get_block(current_block_id) or engine.get_block("start")

    # Validar input según bloque
    if current_block.get("type") == "input":
        validate_input(current_block, payload.message)
        save_as = current_block.get("save_as")
        if save_as:
            state.setdefault("vars", {})[save_as] = payload.message
    elif current_block.get("type") == "options":
        option_ids = {opt["id"] for opt in current_block.get("options", [])}
        if payload.message not in option_ids:
            raise HTTPException(status_code=400, detail="invalid_option")
        save_as = current_block.get("save_as")
        if save_as:
            state.setdefault("vars", {})[save_as] = payload.message
    elif current_block.get("type") == "message":
        pass

    # Intent heuristic o IA (flag use_ia)
    if current_block.get("type") == "input":
        if settings.use_ia:
            inferred = intent.classify(payload.message)  # placeholder IA
        else:
            inferred = intent.classify(payload.message)
        for k, v in inferred.items():
            state.setdefault("vars", {})[k] = v

    # Guardar mensaje del usuario
    save_message(db, session_id, None, "user", payload.message, block_id=current_block_id)

    # Si bloque es appointment, guardar slot elegido y book en agenda
    if current_block.get("type") == "appointment":
        state.setdefault("vars", {})["appointment_slot"] = payload.message
        visit_type = state.get("vars", {}).get("visit_type")
        slot_start = datetime.fromisoformat(payload.message.replace("Z", "+00:00"))
        slot_end = slot_start + timedelta(minutes=30)
        lead = db.query(DBLead).filter(DBLead.session_id == session_id).first()
        lead_id = lead.id if lead else None
        tenant_id = lead.tenant_id if lead else None
        executor.agenda_service.book(db, lead_id, tenant_id, slot_start, slot_end, visit_type)

    next_block_id = engine.next_block(current_block, payload.message)
    if next_block_id:
        state["current_block"] = next_block_id
        session_mgr.save(session_id, state)
        next_block = engine.get_block(next_block_id)
    else:
        next_block = current_block

    lang = pick_lang(flow_data, payload.lang or state.get("lang"))
    state["lang"] = lang
    session_mgr.save(session_id, state)

    # Persist session to DB
    try:
        db_state = db.query(DBSesion).filter(DBSesion.id == session_id).first()
        if db_state:
            db_state.state = state.get("current_block")
            db_state.variables_json = state.get("vars", {})
        else:
            db_state = DBSesion(
                id=session_id,
                tenant_id=None,
                canal="web",
                state=state.get("current_block"),
                variables_json=state.get("vars", {}),
            )
            db.add(db_state)
        db.commit()
    except SQLAlchemyError:
        db.rollback()

    # Crear/actualizar lead en bloque de decisión
    if (next_block_id or current_block_id) == "compute_score_and_decide":
        vars_data = state.get("vars", {})
        scoring_cfg = flow_data.get("scoring", {})
        score, breakdown = compute_score(vars_data, scoring_cfg)
        thresholds = scoring_cfg.get("thresholds", {})
        lead_status = map_score_to_status(score, thresholds)
        try:
            lead = db.query(DBLead).filter(DBLead.session_id == session_id).first()
            if lead:
                lead.score = score
                lead.score_breakdown_json = breakdown
                lead.meta_data = vars_data
                lead.status = lead_status
            else:
                lead = DBLead(
                    tenant_id=None,
                    session_id=session_id,
                    status=lead_status,
                    score=score,
                    score_breakdown_json=breakdown,
                    meta_data=vars_data,
                )
                db.add(lead)
            db.commit()
        except SQLAlchemyError:
            db.rollback()

    def serialize_block(block_id: str, block: dict) -> dict:
        if block is None:
            return {"id": block_id}
        data = dict(block)
        # Seleccionar texto por idioma si es dict
        if "text" in data:
            data["text"] = engine.choose_text(block, lang, flow_data.get("languages", ["es"])[0])
        if data.get("type") == "appointment":
            from datetime import datetime, timedelta

            now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
            slots = [
                (now + timedelta(hours=2)).isoformat() + "Z",
                (now + timedelta(hours=3)).isoformat() + "Z",
                (now + timedelta(hours=4)).isoformat() + "Z",
            ]
            data["slots"] = slots
        return {"id": block_id, **data}

    bot_block_id = next_block_id or current_block_id
    bot_block = serialize_block(bot_block_id, next_block)
    # Si el bloque es appointment, rellenar slots desde estado
    if bot_block.get("type") == "appointment":
        slots_state = state.get("vars", {}).get("available_slots")
        if slots_state:
            bot_block["slots"] = slots_state
    # Ejecutar acciones del bloque
    # Inyectar scoring config en acciones si aplica
    actions = bot_block.get("actions", [])
    for action in actions:
        if action.get("type") == "compute_lead_score":
            action["scoring_config"] = flow_data.get("scoring", {})
    state = executor.execute_actions(actions, session_id, state, db=db)
    session_mgr.save(session_id, state)

    # Guardar mensaje del bot
    save_message(db, session_id, None, "bot", bot_block.get("text") or bot_block["id"], block_id=bot_block["id"])

    # Construir opciones con label en idioma
    opts = []
    for opt in bot_block.get("options", []) or []:
        label = opt.get(f"label_{lang}") or opt.get("label_es") or opt.get("id")
        opts.append({"id": opt.get("id"), "label": label})

    vars_data = state.get("vars", {})
    state_summary = {
        "project_type": vars_data.get("project_type"),
        "budget": vars_data.get("budget"),
        "urgency": vars_data.get("urgency"),
        "lead_score": vars_data.get("lead_score", 0),
    }

    return {
        "session_id": session_id,
        "block_id": bot_block.get("id"),
        "type": bot_block.get("type"),
        "text": bot_block.get("text"),
        "options": opts,
        "state_summary": state_summary,
    }
