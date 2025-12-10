import logging
from typing import Any

from app.services.ai_client import AIClient
from app.services.scoring_service import compute_score
from app.services.agenda_service import AgendaService
from app.services.pricing import get_plan_limits

logger = logging.getLogger(__name__)


class ActionExecutor:
    def __init__(self, settings):
        self.settings = settings
        self.ai_client = AIClient(
            model=settings.ai_model,
            api_key=settings.openai_api_key,
            use_ai=settings.use_ia,
        )
        self.agenda_service = AgendaService()

    def _can_use_ai(self, tenant):
        if not tenant:
            return False
        plan_limits = get_plan_limits(getattr(tenant, "plan", None))
        plan_ai_enabled = (plan_limits.get("features") or {}).get("ia_enabled", True)
        if getattr(tenant, "ia_enabled", None) is False:
            return False
        if getattr(tenant, "use_ia", None) is False:
            return False
        if not plan_ai_enabled:
            return False
        return (tenant.ai_cost or 0) < (tenant.ai_monthly_limit or 0)

    def _register_cost(self, tenant, tokens_in: int, tokens_out: int, db):
        if not tenant or db is None:
            return
        cost = (tokens_in + tokens_out) * float(self.settings.ai_price_per_token_usd)
        tenant.ai_cost = (tenant.ai_cost or 0) + cost
        db.commit()
        return cost

    def execute_actions(self, actions: list[dict], session_id: str, state: dict, db=None):
        """
        Ejecuta stubs de acciones. Modifica el estado cuando aplica (p.ej. end_session).
        """
        for action in actions or []:
            atype = action.get("type")
            logger.info({"event": "action_start", "action": atype, "session_id": session_id, "params": action})
            if atype == "compute_lead_score":
                scoring_cfg = action.get("scoring_config") or {}
                score, breakdown = compute_score(state, scoring_cfg)
                state.setdefault("vars", {})["lead_score"] = score
                state.setdefault("vars", {})["lead_score_breakdown"] = breakdown
                logger.info(
                    {
                        "event": "action_scoring",
                        "session_id": session_id,
                        "score": score,
                        "breakdown": breakdown,
                    }
                )
            elif atype == "create_or_update_lead":
                if db is not None:
                    vars_data = state.get("vars", {})
                    from app.models.leads import Lead
                    from sqlalchemy.exc import SQLAlchemyError

                    try:
                        lead = db.query(Lead).filter(Lead.session_id == session_id).first()
                        if lead:
                            lead.meta_data = vars_data
                            lead.score = vars_data.get("lead_score")
                            lead.score_breakdown_json = vars_data.get("lead_score_breakdown", {})
                        else:
                            lead = Lead(
                                tenant_id=None,
                                session_id=session_id,
                                status="nuevo",
                                score=vars_data.get("lead_score"),
                                score_breakdown_json=vars_data.get("lead_score_breakdown", {}),
                                meta_data=vars_data,
                            )
                            db.add(lead)
                        db.commit()
                    except SQLAlchemyError:
                        db.rollback()
            elif atype == "generate_ai_summary":
                vars_data = state.get("vars", {})
                tenant_id = vars_data.get("tenant_id")
                # Cargar prompt desde DB si existe
                prompt_text = None
                if db is not None and tenant_id:
                    from app.models.ai_prompts import AiPrompt
                    prompt = (
                        db.query(AiPrompt)
                        .filter(AiPrompt.tenant_id == tenant_id, AiPrompt.name == "commercial_brief")
                        .order_by(AiPrompt.version.desc())
                        .first()
                    )
                    if prompt:
                        prompt_text = prompt.prompt_text

                # Control de coste
                tenant = None
                if db is not None and tenant_id:
                    from app.models.tenants import Tenant
                    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()

                if self.settings.use_ia and tenant and self._can_use_ai(tenant):
                    summary, tokens_in, tokens_out = self.ai_client.generate_commercial_brief(vars_data, prompt_text)
                    cost = self._register_cost(tenant, tokens_in, tokens_out, db)
                    logger.info(
                        {
                            "event": "ai_summary_generated",
                            "session_id": session_id,
                            "tenant_id": tenant_id,
                            "tokens_in": tokens_in,
                            "tokens_out": tokens_out,
                            "cost": cost,
                        }
                    )
                else:
                    summary, tokens_in, tokens_out = self.ai_client.generate_commercial_brief(vars_data, prompt_text)
                    logger.info(
                        {
                            "event": "ai_summary_fallback",
                            "session_id": session_id,
                            "tenant_id": tenant_id,
                            "tokens_in": tokens_in,
                            "tokens_out": tokens_out,
                        }
                    )
                state.setdefault("vars", {})["ai_summary"] = summary
            elif atype == "generate_pdf":
                # Stub: solo marca placeholder
                state.setdefault("vars", {})["summary_pdf"] = "s3://stub/summary.pdf"
            elif atype == "notify_team":
                # Stub: loguea notificación
                logger.info({"event": "notify_team_stub", "session_id": session_id, "payload": action})
            elif atype == "load_available_slots":
                slots = self.agenda_service.get_slots(
                    tenant_id=state.get("vars", {}).get("tenant_id"),
                    visit_type=state.get("vars", {}).get("visit_type"),
                    location=state.get("vars", {}).get("location"),
                )
                state.setdefault("vars", {})["available_slots"] = slots
            elif atype == "book_appointment":
                # La creación en DB se maneja cuando el usuario envía el slot; aquí aseguramos slots en estado.
                if state.get("vars", {}).get("available_slots") is None:
                    slots = self.agenda_service.get_slots(
                        tenant_id=state.get("vars", {}).get("tenant_id"),
                        visit_type=state.get("vars", {}).get("visit_type"),
                        location=state.get("vars", {}).get("location"),
                    )
                    state.setdefault("vars", {})["available_slots"] = slots
            elif atype == "end_session":
                state["ended"] = True
            elif atype in {"generate_ai_welcome", "generate_ai_closing", "generate_ai_micro_proposal"}:
                vars_data = state.get("vars", {})
                tenant_id = vars_data.get("tenant_id")
                tenant = None
                if db is not None and tenant_id:
                    from app.models.tenants import Tenant

                    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
                flags = tenant.flags_ia if tenant and tenant.flags_ia else {}
                if flags.get("text_gen_enabled") and self._can_use_ai(tenant):
                    kind = (
                        "welcome"
                        if atype == "generate_ai_welcome"
                        else "closing"
                        if atype == "generate_ai_closing"
                        else "micro_proposal"
                    )
                    text, tokens_in, tokens_out = self.ai_client.generate_text_snippet(kind, vars_data)
                    cost = self._register_cost(tenant, tokens_in, tokens_out, db)
                    state.setdefault("vars", {})[f"{kind}_text"] = text
                    logger.info(
                        {
                            "event": "ai_text_generated",
                            "kind": kind,
                            "session_id": session_id,
                            "tenant_id": tenant_id,
                            "tokens_in": tokens_in,
                            "tokens_out": tokens_out,
                            "cost": cost,
                        }
                    )
                else:
                    kind = (
                        "welcome"
                        if atype == "generate_ai_welcome"
                        else "closing"
                        if atype == "generate_ai_closing"
                        else "micro_proposal"
                    )
                    text = self.ai_client._deterministic_snippet(kind, vars_data)
                    state.setdefault("vars", {})[f"{kind}_text"] = text
            logger.info({"event": "action_end", "action": atype, "session_id": session_id})
        return state
