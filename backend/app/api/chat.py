import asyncio
import json
import os
import re
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Header, status
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
from app.observability import metrics
from app.models.sessions import Session as DBSesion
from app.models.leads import Lead as DBLead
from app.models.messages import Message as DBMessage
from app.models.tenants import Tenant, UsageMode, BillingStatus
from app.services.ia_usage_service import IAQuotaExceeded
from app.services.pii_service import PIIService
from app.observability.tracing import start_span, end_span, set_request_context
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta, timezone
from app.services.plan_limits import require_active_subscription
from app.services.pricing import get_plan_limits
from app.services.quota_service import QuotaService

try:
    from app.services.ai.ai_engine import ai_extract, ai_reply, last_ai_fallback
except Exception:
    ai_extract = ai_reply = last_ai_fallback = None

router = APIRouter(prefix="/chat", tags=["chat"])
pii_service = PIIService()
PII_AUTO_UPGRADE = os.getenv("PII_AUTO_UPGRADE") == "1"


class ChatInput(BaseModel):
    message: str
    session_id: Optional[str] = None
    lang: Optional[str] = None


def _register_ai_fallback(state: dict, reason: str | None, session_id: str | None, tenant_id: str | None):
    if not reason:
        return
    if state.get("ai_fallback_reason"):
        return
    state["ai_fallback_reason"] = reason
    logger.warning(
        {
            "event": "ai_fallback",
            "session_id": session_id,
            "tenant_id": tenant_id,
            "reason": reason,
        }
    )


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
        nums = [
            float(n.replace(",", ".")) for n in re.findall(r"\d+[.,]?\d*", user_input)
        ]
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
        nums = [
            float(n.replace(",", ".")) for n in re.findall(r"\d+[.,]?\d*", user_input)
        ]
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


def save_message(
    db,
    session_id: str,
    tenant_id,
    role: str,
    content: str,
    block_id: Optional[str] = None,
    ai_meta=None,
):
    enc_content = content
    pii_version = 1
    if role == "user":
        enc_content, changed = pii_service.encrypt_message_content(
            content, str(tenant_id)
        )
        if not changed:
            pii_version = 1
    try:
        msg = DBMessage(
            tenant_id=tenant_id,
            session_id=session_id,
            role=role,
            content=enc_content,
            block_id=block_id,
            ai_meta=ai_meta or {},
            attachments=[],
            pii_version=pii_version,
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


@router.get(
    "/history/{session_id}",
    dependencies=[Depends(require_auth), Depends(require_active_subscription)],
)
def get_history(
    session_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    msgs = (
        db.query(DBMessage)
        .filter(DBMessage.session_id == session_id, DBMessage.tenant_id == tenant_id)
        .order_by(DBMessage.id.asc())
        .all()
    )
    items = []
    for m in msgs:
        content = m.content
        if pii_service.is_encrypted(content):
            content = pii_service.decrypt_pii(content)
        elif PII_AUTO_UPGRADE:
            enc, changed = pii_service.encrypt_message_content(content, str(tenant_id))
            if changed:
                try:
                    m.content = enc
                    m.pii_version = 1
                    db.add(m)
                    db.commit()
                    content = pii_service.decrypt_pii(enc)
                except SQLAlchemyError:
                    db.rollback()
        items.append(
            {
                "role": m.role,
                "content": content,
                "block_id": m.block_id,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
        )
    return items


@router.post(
    "/send",
    dependencies=[Depends(require_auth), Depends(require_active_subscription)],
)
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
    if tenant is None and os.getenv("DISABLE_DB") == "1":
        class _Stub:
            id = tenant_id
            plan = "BASE"
            ia_enabled = True
            use_ia = True
            billing_status = BillingStatus.ACTIVE
            flags_ia = {}
        tenant = _Stub()
    try:
        quota_status = QuotaService.enforce(db, tenant)
    except HTTPException as exc:
        if exc.status_code == status.HTTP_402_PAYMENT_REQUIRED:
            detail = exc.detail if isinstance(exc.detail, dict) else {}
            quota_payload = detail.get("quota_status") if isinstance(detail, dict) else None
            quota_mode = (
                quota_payload.get("mode") if isinstance(quota_payload, dict) else "LOCKED"
            ) or "LOCKED"
            fallback_response = {
                "message": detail.get("message") or QuotaService.LOCKED_MESSAGE,
                "quota_status": quota_mode,
                "saving_mode": False,
                "needs_upgrade_notice": True,
                "cta": detail.get("cta") or QuotaService.CTA_UPGRADE,
            }
            idemp_store.set(idempotency_key, fallback_response)
            return fallback_response
        raise
    plan_value = getattr(tenant, "plan", None)
    if plan_value and hasattr(plan_value, "value"):
        plan_value = plan_value.value
    plan_value = plan_value or "base"
    flow_data = load_flow_for_plan(plan_value)
    flags = tenant.flags_ia if tenant else {}
    plan_limits = get_plan_limits(plan_value)
    plan_ai_enabled = (plan_limits.get("features") or {}).get("ia_enabled", True)
    tenant_ai_enabled = getattr(tenant, "ia_enabled", None)
    if tenant_ai_enabled is None:
        tenant_ai_enabled = getattr(tenant, "use_ia", None)
    if tenant_ai_enabled is None:
        tenant_ai_enabled = True
    flags_enabled = flags.get("intent_extraction_enabled", True) if tenant else True
    use_ai_intent = bool(
        settings.use_ia and plan_ai_enabled and tenant_ai_enabled and flags_enabled
    )
    ai_extractor = (
        AIExtractor(settings.openai_api_key, settings.ai_model)
        if use_ai_intent
        else None
    )
    intent = IntentClassifier(ai_extractor=ai_extractor)
    executor = ActionExecutor(settings)
    ai_extract_meta = None
    ai_reply_text = None

    session_id = payload.session_id or str(uuid4())
    set_request_context(
        tenant_id=tenant_id,
        session_id=session_id,
    )
    metrics.set_gauge("chat_sessions_active", 1, {"tenant_id": tenant_id})
    state = session_mgr.load(session_id) or {}
    if state and state.get("vars", {}).get("tenant_id") not in (None, tenant_id):
        raise HTTPException(status_code=403, detail="tenant_mismatch")
    if not state:
        # Intentar cargar desde DB si existe
        db_state = (
            db.query(DBSesion)
            .filter(DBSesion.id == session_id, DBSesion.tenant_id == tenant_id)
            .first()
        )
        if db_state:
            vars_data = db_state.variables_json or {}
            vars_data.setdefault("tenant_id", tenant_id)
            state = {
                "current_block": db_state.state
                or flow_data.get("start_block", "start"),
                "vars": vars_data,
            }
            session_mgr.save(session_id, state)
        else:
            state = {
                "current_block": flow_data.get("start_block", "start"),
                "vars": {"tenant_id": tenant_id},
            }
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

    if not use_ai_intent:
        _register_ai_fallback(state, "ai_disabled", session_id, tenant_id)

    engine = FlowEngine(flow_data, context=state.get("vars", {}))
    start_block = flow_data.get("start_block", "start")
    current_block_id = state.get("current_block", start_block)
    current_block = engine.get_block(current_block_id) or engine.get_block(start_block)
    if not current_block:
        # fallback duro al primer bloque disponible
        first_block_id = next(iter(flow_data.get("blocks", {}) or {"start": {}}))
        current_block = engine.get_block(first_block_id) or {
            "id": first_block_id,
            "type": "message",
        }
        state["current_block"] = first_block_id

    span_id = start_span(f"chat_step_{current_block.get('id')}")

    # Validar input según bloque
    block_type = current_block.get("type")
    save_key = current_block.get("save_as") or current_block.get("save_to")
    if block_type in ("input",):
        validate_input(current_block, payload.message)
        if save_key:
            state.setdefault("vars", {})[save_key] = payload.message
    elif block_type in ("options", "buttons"):
        options_list = current_block.get("options", []) or []
        option_ids = [
            opt.get("id") or opt.get("value") or opt.get("label")
            for opt in options_list
        ]
        chosen = (
            payload.message
            if payload.message in option_ids
            else (option_ids[0] if option_ids else payload.message)
        )
        if save_key:
            state.setdefault("vars", {})[save_key] = chosen
        payload.message = chosen
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
            ai_extract_meta = (
                asyncio.run(
                    ai_extract(
                        payload.message,
                        purpose="extraction",
                        tenant=tenant,
                        tenant_id=tenant_id,
                        language=payload.lang or state.get("lang"),
                        db=db,
                        session_id=session_id,
                    )
                )
                or None
            )
            if isinstance(ai_extract_meta, dict) and ai_extract_meta:
                state.setdefault("vars", {})["ai_extract"] = ai_extract_meta
                _hydrate_from_ai_extract(state, ai_extract_meta)
            if last_ai_fallback:
                _register_ai_fallback(
                    state, last_ai_fallback(), session_id, tenant_id
                )
        except IAQuotaExceeded as exc:
            _register_ai_fallback(state, "ia_quota_exceeded", session_id, tenant_id)
            logger.warning({"event": "ai_extract_quota_blocked", "error": str(exc)})
            ai_extract_meta = None
        except Exception as exc:
            logger.warning({"event": "ai_extract_failed", "error": str(exc)})
            _register_ai_fallback(state, "ai_extract_error", session_id, tenant_id)
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
    save_message(
        db,
        session_id,
        tenant_id,
        "user",
        payload.message,
        block_id=current_block_id,
        ai_meta=ai_extract_meta,
    )

    # Si bloque es appointment, guardar slot elegido y book en agenda
    if current_block.get("type") == "appointment":
        state.setdefault("vars", {})["appointment_slot"] = payload.message
        visit_type = state.get("vars", {}).get("visit_type")
        slot_start = datetime.fromisoformat(payload.message.replace("Z", "+00:00"))
        slot_end = slot_start + timedelta(minutes=30)
        lead = (
            db.query(DBLead)
            .filter(DBLead.session_id == session_id, DBLead.tenant_id == tenant_id)
            .first()
        )
        lead_id = lead.id if lead else None
        lead_tenant = lead.tenant_id if lead else tenant_id
        executor.agenda_service.book(
            db, lead_id, lead_tenant, slot_start, slot_end, visit_type
        )

    next_block_id = engine.next_block(current_block, payload.message)
    if next_block_id:
        state["current_block"] = next_block_id
        session_mgr.save(session_id, state)
        next_block = engine.get_block(next_block_id)
    else:
        next_block = current_block

    # Si seguimos en el mismo bloque y ya hay valor guardado, avanzar forzando con ese valor
    current_save_key = current_block.get("save_as") or current_block.get("save_to")
    if (
        next_block_id == current_block_id
        and current_save_key
        and state.get("vars", {}).get(current_save_key)
    ):
        forced_val = state.get("vars", {}).get(current_save_key)
        forced_next = engine.next_block(current_block, forced_val) or current_block.get(
            "next"
        )
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
        skip_val = state.get("vars", {}).get(
            next_block.get("save_as") or next_block.get("save_to")
        )
        next_block_id = engine.next_block(next_block, skip_val) or next_block.get(
            "next"
        )
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
        db_state = (
            db.query(DBSesion)
            .filter(DBSesion.id == session_id, DBSesion.tenant_id == tenant_id)
            .first()
        )
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
        encrypted_meta, _ = pii_service.encrypt_meta(vars_data, tenant_id)
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
            lead = (
                db.query(DBLead)
                .filter(DBLead.session_id == session_id, DBLead.tenant_id == tenant_id)
                .first()
            )
            if lead:
                lead.score = score
                lead.score_breakdown_json = breakdown
                lead.meta_data = encrypted_meta
                lead.pii_version = 1
                lead.status = lead_status
            else:
                lead = DBLead(
                    tenant_id=tenant_id,
                    session_id=session_id,
                    status=lead_status,
                    score=score,
                    score_breakdown_json=breakdown,
                    meta_data=encrypted_meta,
                    pii_version=1,
                )
                db.add(lead)
                metrics.inc_counter(
                    "leads_created_total",
                    {"tenant_id": tenant_id, "source": "chat"},
                )
            db.commit()
            try:
                from app.services.pdf_service import PDFService

                pdf_service = PDFService()
                extracted_data = vars_data or {}
                ia_output = state.get("vars", {}).get("ai_summary") or {}
                pdf_service.generate_commercial_pdf(
                    lead,
                    tenant,
                    extracted_data,
                    ia_output if isinstance(ia_output, dict) else {},
                )
                pdf_service.generate_operational_pdf(
                    lead,
                    tenant,
                    extracted_data,
                    ia_output if isinstance(ia_output, dict) else {},
                )
            except Exception as pdf_exc:
                logger.warning(
                    {"event": "pdf_generation_failed", "error": str(pdf_exc)}
                )
        except SQLAlchemyError:
            db.rollback()

    def serialize_block(block_id: str, block: dict) -> dict:
        if block is None:
            return {"id": block_id}
        data = dict(block)
        # Seleccionar texto por idioma si es dict
        if "text" in data:
            data["text"] = engine.choose_text(
                block, lang, flow_data.get("languages", ["es"])[0]
            )
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
            if not ai_extract or not use_ai_intent:
                break
            source_text = (
                payload.message or state.get("vars", {}).get("area_descripcion") or ""
            )
            field = current.get("field") or "ai_field"
            try:
                ai_data = (
                    asyncio.run(
                            ai_extract(
                                source_text,
                                purpose="dimensions",
                                tenant=tenant,
                                tenant_id=tenant_id,
                                language=lang,
                                db=db,
                            )
                        )
                        or {}
                    )
                if isinstance(ai_data, dict):
                    val = (
                        ai_data.get("metros")
                        or ai_data.get(field)
                        or ai_data.get("value")
                    )
                    if val is not None:
                        state.setdefault("vars", {})[field] = val
            except Exception as exc:
                logger.warning(
                    {"event": "ai_extract_autoblock_failed", "error": str(exc)}
                )
            next_id = current.get("next") or current.get("next_map", {}).get("default")
            if not next_id:
                return current
            state["current_block"] = next_id
            session_mgr.save(session_id, state)
            current = engine.get_block(next_id)
        return current

    next_block = run_auto_blocks(next_block)

    bot_block_id = (
        state.get("current_block", next_block_id or current_block_id)
        or current_block_id
    )
    bot_block = serialize_block(bot_block_id, next_block)
    # Si el bloque es ai_generate, generar texto IA y usar fallback si falla
    if bot_block.get("type") == "ai_generate":
        fallback_text = bot_block.get("fallback_text")
        if ai_reply and use_ai_intent:
            prompt_text = bot_block.get("prompt") or ""
            try:
                ai_text = asyncio.run(
                    ai_reply(
                        prompt_text,
                        {"prompt": prompt_text},
                        purpose="custom_prompt",
                        tenant=tenant,
                        tenant_id=tenant_id,
                        language=lang,
                        db=db,
                        session_id=session_id,
                    )
                )
                if ai_text:
                    bot_block["text"] = ai_text
                if last_ai_fallback:
                    _register_ai_fallback(
                        state, last_ai_fallback(), session_id, tenant_id
                    )
            except IAQuotaExceeded as exc:
                _register_ai_fallback(
                    state, "ia_quota_exceeded", session_id, tenant_id
                )
                logger.warning({"event": "ai_generate_quota_blocked", "error": str(exc)})
            except Exception as exc:
                logger.warning({"event": "ai_generate_failed", "error": str(exc)})
        if not bot_block.get("text") and isinstance(fallback_text, dict):
            bot_block["text"] = fallback_text.get(lang) or fallback_text.get(
                flow_data.get("languages", ["es"])[0]
            )
        if not bot_block.get("text"):
            bot_block["text"] = (
                bot_block.get("fallback_text") or bot_block.get("text") or ""
            )
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
    if state.get("ended"):
        metrics.inc_counter(
            "flow_conversations_completed_total", {"tenant_id": tenant_id}
        )
    session_mgr.save(session_id, state)
    if ai_reply and use_ai_intent:
        simple_context = {"vars": state.get("vars", {}), "bot_block": bot_block}
        try:
            ai_reply_text = (
                asyncio.run(
                    ai_reply(
                        payload.message,
                        simple_context,
                        purpose="reply_contextual",
                        tenant=tenant,
                        tenant_id=tenant_id,
                        language=lang,
                        db=db,
                        session_id=session_id,
                    )
                )
                or None
            )
            if last_ai_fallback:
                _register_ai_fallback(
                    state, last_ai_fallback(), session_id, tenant_id
                )
        except IAQuotaExceeded as exc:
            _register_ai_fallback(state, "ia_quota_exceeded", session_id, tenant_id)
            logger.warning({"event": "ai_reply_quota_blocked", "error": str(exc)})
            ai_reply_text = None
        except Exception as exc:
            logger.warning({"event": "ai_reply_failed", "error": str(exc)})
            ai_reply_text = None
            _register_ai_fallback(state, "ai_reply_error", session_id, tenant_id)

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
        label = (
            opt.get(f"label_{lang}")
            or opt.get("label_es")
            or opt.get("label")
            or opt.get("value")
            or opt.get("id")
        )
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
    if quota_status:
        response_data["quota_status"] = quota_status.mode.value
        response_data["quota_details"] = quota_status.to_dict()
        response_data["needs_upgrade_notice"] = bool(
            getattr(quota_status, "needs_upgrade_notice", False)
        )
        if quota_status.mode == UsageMode.SAVING:
            response_data["saving_mode"] = True
    idemp_store.set(idempotency_key, response_data)
    end_span()
    return response_data
