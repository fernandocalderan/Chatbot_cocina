import asyncio
import json
import re
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from loguru import logger

from app.api.auth import oauth2_scheme, require_auth
from app.api.deps import get_db, get_tenant_id
from app.core.config import get_settings
from app.core.flow_engine import FlowEngine
from app.core.session_manager import SessionManager
from app.core.intent_classifier import IntentClassifier
from app.core.ai_extractor import AIExtractor
from app.core.actions import ActionExecutor
from app.core.idempotency import IdempotencyStore
from app.models.sessions import Session as DBSesion
from app.models.leads import Lead as DBLead
from app.models.messages import Message as DBMessage
from app.models.tenants import Tenant
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta, timezone

try:
    from app.services.ai.ai_engine import ai_extract, ai_reply
except Exception:
    ai_extract = ai_reply = None

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatInput(BaseModel):
    message: str
    session_id: Optional[str] = None
    lang: Optional[str] = None


def load_flow_for_plan(plan: str | None) -> dict:
    flow_dir = Path(__file__).resolve().parent.parent / "flows"
    plan_norm = (plan or "base").lower()
    filename = {
        "base": "base_plan_fixed.json",
        "pro": "pro_plan_fixed.json",
        "elite": "elite_plan_fixed.json",
    }.get(plan_norm, "base_plan_fixed.json")
    flow_path = flow_dir / filename
    if not flow_path.exists():
        # fallback
        flow_path = flow_dir / "base_plan_fixed.json"
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
        if not re.match(r"^\+?\d{7,15}$", user_input.strip()):
            raise HTTPException(status_code=400, detail="invalid_phone")
    elif vtype == "email_optional":
        if user_input.strip() == "":
            return
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", user_input.strip()):
            raise HTTPException(status_code=400, detail="invalid_email")
    elif vtype == "area_m2":
        nums = [float(n.replace(",", ".")) for n in re.findall(r"\d+[.,]?\d*", user_input)]
        if not nums:
            raise HTTPException(status_code=400, detail="invalid_area")
        area = nums[0]
        if len(nums) >= 2:
            area = nums[0] * nums[1]
        min_m2 = float(validation.get("min_m2", 0.5))
        max_m2 = float(validation.get("max_m2", 300.0))
        if not (min_m2 <= area <= max_m2):
            raise HTTPException(status_code=400, detail="invalid_area")
    elif vtype == "budget":
        nums = [float(n.replace(",", ".")) for n in re.findall(r"\d+[.,]?\d*", user_input)]
        if not nums:
            raise HTTPException(status_code=400, detail="invalid_budget")
        min_budget = float(validation.get("min_budget", 500))
        max_budget = float(validation.get("max_budget", 300000))
        low = min(nums)
        high = max(nums)
        if low > high or low < min_budget or high > max_budget:
            raise HTTPException(status_code=400, detail="invalid_budget")


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

def _hydrate_from_ai_extract(state: dict, ai_data: dict | None):
    """Map AI extraction fields to flow variables to avoid repreguntas."""
    if not isinstance(ai_data, dict):
        return
    vars_ref = state.setdefault("vars", {})
    # Map posibles claves devueltas por prompts avanzados/genéricos
    mapping = {
        "metros": "measures",
        "measures": "measures",
        "estilo": "style",
        "style": "style",
        "presupuesto": "budget",
        "budget": "budget",
        "urgencia": "urgency",
        "urgency": "urgency",
        "project_type": "project_type",
    }
    for src, dest in mapping.items():
        val = ai_data.get(src)
        if val and dest not in vars_ref:
            vars_ref[dest] = val

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


@router.get("/history/{session_id}", dependencies=[Depends(require_auth)])
def get_history(session_id: str, db=Depends(get_db), tenant_id: str = Depends(get_tenant_id), token: str = Depends(oauth2_scheme)):
    msgs = (
        db.query(DBMessage)
        .filter(DBMessage.session_id == session_id, DBMessage.tenant_id == tenant_id)
        .order_by(DBMessage.id.asc())
        .all()
    )
    return [
        {"role": m.role, "content": m.content, "block_id": m.block_id, "created_at": m.created_at.isoformat() if m.created_at else None}
        for m in msgs
    ]


@router.post("/send", dependencies=[Depends(require_auth)])
def send_message(
    payload: ChatInput,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    tenant_id: str = Depends(get_tenant_id),
    db=Depends(get_db),
    token: str = Depends(oauth2_scheme),
):  # db kept for future use
    settings = get_settings()
    if not idempotency_key:
        # Autogenera uno si el cliente no lo envía
        idempotency_key = str(uuid4())

    idemp_store = IdempotencyStore(settings.redis_url)
    existing = idemp_store.get(idempotency_key)
    if existing is not None:
        return existing

    session_mgr = SessionManager(settings.redis_url)
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    plan_value = tenant.plan if tenant else "base"
    flow_data = load_flow_for_plan(plan_value)
    engine = FlowEngine(flow_data)
    flags = tenant.flags_ia if tenant else {}
    use_ai_intent = bool(flags.get("intent_extraction_enabled") or settings.use_ia)
    ai_extractor = AIExtractor(settings.openai_api_key, settings.ai_model) if use_ai_intent else None
    intent = IntentClassifier(ai_extractor=ai_extractor)
    executor = ActionExecutor(settings)
    ai_extract_meta = None
    ai_reply_text = None

    session_id = payload.session_id or str(uuid4())
    state = session_mgr.load(session_id) or {}
    if state and state.get("vars", {}).get("tenant_id") not in (None, tenant_id):
        raise HTTPException(status_code=403, detail="tenant_mismatch")
    if not state:
        # Intentar cargar desde DB si existe
        db_state = db.query(DBSesion).filter(DBSesion.id == session_id, DBSesion.tenant_id == tenant_id).first()
        if db_state:
            vars_data = db_state.variables_json or {}
            vars_data.setdefault("tenant_id", tenant_id)
            state = {"current_block": db_state.state or flow_data.get("start_block", "start"), "vars": vars_data}
            session_mgr.save(session_id, state)
        else:
            state = {"current_block": flow_data.get("start_block", "start"), "vars": {"tenant_id": tenant_id}}
            session_mgr.save(session_id, state)
            try:
                db_obj = DBSesion(
                    id=session_id,
                    tenant_id=tenant_id,
                    canal="web",
                    state=state.get("current_block"),
                    variables_json=state.get("vars", {}),
                )
                db.add(db_obj)
                db.commit()
            except SQLAlchemyError:
                db.rollback()
    else:
        state.setdefault("vars", {}).setdefault("tenant_id", tenant_id)

    start_block = flow_data.get("start_block", "start")
    current_block_id = state.get("current_block", start_block)
    current_block = engine.get_block(current_block_id) or engine.get_block("start")

    # Validar input según bloque
    block_type = current_block.get("type")
    save_key = current_block.get("save_as") or current_block.get("save_to")
    if block_type in ("input",):
        validate_input(current_block, payload.message)
        if save_key:
            state.setdefault("vars", {})[save_key] = payload.message
    elif block_type in ("options", "buttons"):
        option_ids = {opt.get("id") or opt.get("value") or opt.get("label") for opt in current_block.get("options", [])}
        if payload.message not in option_ids:
            raise HTTPException(status_code=400, detail="invalid_option")
        if save_key:
            state.setdefault("vars", {})[save_key] = payload.message
    elif block_type == "appointment":
        try:
            slot_dt = datetime.fromisoformat(payload.message.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=400, detail="invalid_appointment_slot")
        now = datetime.now(timezone.utc) - timedelta(minutes=5)
        future_limit = now + timedelta(days=365)
        if slot_dt < now or slot_dt > future_limit:
            raise HTTPException(status_code=400, detail="invalid_appointment_slot")
        state.setdefault("vars", {})["appointment_slot"] = payload.message
    elif block_type == "attachment":
        # payload.message expected to be file_id or s3_key reference
        save_as = current_block.get("save_as") or "attachment"
        state.setdefault("vars", {}).setdefault("attachments", [])
        state["vars"]["attachments"].append({save_as: payload.message})
    elif block_type == "message":
        pass

    # Intent heuristic o IA (flag use_ia)
    if current_block.get("type") == "input":
        inferred = intent.classify(payload.message, use_ai=use_ai_intent)
        for k, v in inferred.items():
            state.setdefault("vars", {})[k] = v
    if ai_extract and use_ai_intent:
        try:
            ai_extract_meta = asyncio.run(
                ai_extract(
                    payload.message,
                    purpose="extraction",
                    tenant_id=tenant_id,
                    language=payload.lang or state.get("lang"),
                )
            ) or None
            if isinstance(ai_extract_meta, dict) and ai_extract_meta:
                state.setdefault("vars", {})["ai_extract"] = ai_extract_meta
                _hydrate_from_ai_extract(state, ai_extract_meta)
        except Exception as exc:
            logger.warning({"event": "ai_extract_failed", "error": str(exc)})
            ai_extract_meta = None

    logger.info(
        {
            "event": "chat_send_input",
            "session_id": session_id,
            "tenant_id": state.get("vars", {}).get("tenant_id"),
            "block_id": current_block_id,
            "message": payload.message,
        }
    )
    # Guardar mensaje del usuario
    save_message(db, session_id, tenant_id, "user", payload.message, block_id=current_block_id, ai_meta=ai_extract_meta)

    # Si bloque es appointment, guardar slot elegido y book en agenda
    if current_block.get("type") == "appointment":
        state.setdefault("vars", {})["appointment_slot"] = payload.message
        visit_type = state.get("vars", {}).get("visit_type")
        slot_start = datetime.fromisoformat(payload.message.replace("Z", "+00:00"))
        slot_end = slot_start + timedelta(minutes=30)
        lead = db.query(DBLead).filter(DBLead.session_id == session_id, DBLead.tenant_id == tenant_id).first()
        lead_id = lead.id if lead else None
        lead_tenant = lead.tenant_id if lead else tenant_id
        executor.agenda_service.book(db, lead_id, lead_tenant, slot_start, slot_end, visit_type)

    next_block_id = engine.next_block(current_block, payload.message)
    if next_block_id:
        state["current_block"] = next_block_id
        session_mgr.save(session_id, state)
        next_block = engine.get_block(next_block_id)
    else:
        next_block = current_block

    # Si seguimos en el mismo bloque y ya hay valor guardado, avanzar forzando con ese valor
    current_save_key = current_block.get("save_as") or current_block.get("save_to")
    if next_block_id == current_block_id and current_save_key and state.get("vars", {}).get(current_save_key):
        forced_val = state.get("vars", {}).get(current_save_key)
        forced_next = engine.next_block(current_block, forced_val) or current_block.get("next")
        if forced_next:
            state["current_block"] = forced_next
            session_mgr.save(session_id, state)
            next_block = engine.get_block(forced_next) or next_block

    # Si ya tenemos la variable de un bloque input/options, saltarlo para evitar repreguntas
    def should_skip(block: dict) -> bool:
        if not block:
            return False
        if block.get("type") not in ("input", "options", "buttons"):
            return False
        save_as = block.get("save_as") or block.get("save_to")
        return bool(save_as and state.get("vars", {}).get(save_as))

    while should_skip(next_block):
        skip_val = state.get("vars", {}).get(next_block.get("save_as") or next_block.get("save_to"))
        next_block_id = engine.next_block(next_block, skip_val) or next_block.get("next")
        if not next_block_id:
            break
        state["current_block"] = next_block_id
        session_mgr.save(session_id, state)
        next_block = engine.get_block(next_block_id)

    lang = pick_lang(flow_data, payload.lang or state.get("lang"))
    state["lang"] = lang
    session_mgr.save(session_id, state)

    # Persist session to DB
    try:
        db_state = db.query(DBSesion).filter(DBSesion.id == session_id, DBSesion.tenant_id == tenant_id).first()
        if db_state:
            db_state.state = state.get("current_block")
            db_state.variables_json = state.get("vars", {})
            if not db_state.tenant_id:
                db_state.tenant_id = tenant_id
        else:
            db_state = DBSesion(
                id=session_id,
                tenant_id=tenant_id,
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
        logger.info(
            {
                "event": "scoring_applied",
                "session_id": session_id,
                "tenant_id": state.get("vars", {}).get("tenant_id"),
                "score": score,
                "breakdown": breakdown,
            }
        )
        try:
            lead = db.query(DBLead).filter(DBLead.session_id == session_id, DBLead.tenant_id == tenant_id).first()
            if lead:
                lead.score = score
                lead.score_breakdown_json = breakdown
                lead.meta_data = vars_data
                lead.status = lead_status
            else:
                lead = DBLead(
                    tenant_id=tenant_id,
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

            now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
            slots = [
                (now + timedelta(hours=2)).isoformat() + "Z",
                (now + timedelta(hours=3)).isoformat() + "Z",
                (now + timedelta(hours=4)).isoformat() + "Z",
            ]
            data["slots"] = slots
        return {"id": block_id, **data}

    # Ejecutar bloques automáticos (ai_extract) antes de responder al usuario
    def run_auto_blocks(block):
        nonlocal state
        current = block
        while current and current.get("type") == "ai_extract":
            source_text = payload.message or state.get("vars", {}).get("area_descripcion") or ""
            field = current.get("field") or "ai_field"
            try:
                ai_data = asyncio.run(
                    ai_extract(
                        source_text,
                        purpose="dimensions",
                        tenant_id=tenant_id,
                        language=lang,
                    )
                ) or {}
                if isinstance(ai_data, dict):
                    val = ai_data.get("metros") or ai_data.get(field) or ai_data.get("value")
                    if val is not None:
                        state.setdefault("vars", {})[field] = val
            except Exception as exc:
                logger.warning({"event": "ai_extract_autoblock_failed", "error": str(exc)})
            next_id = current.get("next") or current.get("next_map", {}).get("default")
            if not next_id:
                return current
            state["current_block"] = next_id
            session_mgr.save(session_id, state)
            current = engine.get_block(next_id)
        return current

    next_block = run_auto_blocks(next_block)

    bot_block_id = state.get("current_block", next_block_id or current_block_id) or current_block_id
    bot_block = serialize_block(bot_block_id, next_block)
    # Si el bloque es ai_generate, generar texto IA y usar fallback si falla
    if bot_block.get("type") == "ai_generate" and ai_reply and use_ai_intent:
        prompt_text = bot_block.get("prompt") or ""
        fallback_text = bot_block.get("fallback_text")
        try:
            ai_text = asyncio.run(
                ai_reply(
                    prompt_text,
                    {"prompt": prompt_text},
                    purpose="custom_prompt",
                    tenant_id=tenant_id,
                    language=lang,
                )
            )
            if ai_text:
                bot_block["text"] = ai_text
        except Exception as exc:
            logger.warning({"event": "ai_generate_failed", "error": str(exc)})
        if not bot_block.get("text") and isinstance(fallback_text, dict):
            bot_block["text"] = fallback_text.get(lang) or fallback_text.get(flow_data.get("languages", ["es"])[0])
        bot_block["type"] = "message"
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
    if ai_reply and use_ai_intent:
        simple_context = {"vars": state.get("vars", {}), "bot_block": bot_block}
        try:
            ai_reply_text = asyncio.run(
                ai_reply(
                    payload.message,
                    simple_context,
                    purpose="reply_contextual",
                    tenant_id=tenant_id,
                    language=lang,
                )
            ) or None
        except Exception as exc:
            logger.warning({"event": "ai_reply_failed", "error": str(exc)})
            ai_reply_text = None

    # Guardar mensaje del bot
    bot_ai_meta = {"ai_reply": ai_reply_text} if ai_reply_text else None
    save_message(
        db,
        session_id,
        tenant_id,
        "bot",
        bot_block.get("text") or bot_block["id"],
        block_id=bot_block["id"],
        ai_meta=bot_ai_meta,
    )
    logger.info(
        {
            "event": "chat_send_output",
            "session_id": session_id,
            "tenant_id": state.get("vars", {}).get("tenant_id"),
            "block_id": bot_block.get("id"),
            "type": bot_block.get("type"),
            "text": bot_block.get("text"),
        }
    )

    # Construir opciones con label en idioma
    opts = []
    for opt in bot_block.get("options", []) or []:
        label = opt.get(f"label_{lang}") or opt.get("label_es") or opt.get("label") or opt.get("value") or opt.get("id")
        opt_id = opt.get("id") or opt.get("value") or opt.get("label")
        opts.append({"id": opt_id, "label": label})

    vars_data = state.get("vars", {})
    state_summary = {
        "project_type": vars_data.get("project_type"),
        "budget": vars_data.get("budget"),
        "urgency": vars_data.get("urgency"),
        "lead_score": vars_data.get("lead_score", 0),
    }

    response_data = {
        "session_id": session_id,
        "block_id": bot_block.get("id"),
        "type": bot_block.get("type"),
        "text": bot_block.get("text"),
        "options": opts,
        "state_summary": state_summary,
    }
    if ai_reply_text:
        response_data["ai_reply"] = ai_reply_text
    idemp_store.set(idempotency_key, response_data)
    return response_data
