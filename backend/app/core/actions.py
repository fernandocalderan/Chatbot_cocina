import logging
from typing import Any

from app.services.ai_client import AIClient
from app.services.scoring_service import compute_score
from app.services.agenda_service import AgendaService

logger = logging.getLogger(__name__)


class ActionExecutor:
    def __init__(self, settings):
        self.settings = settings
        self.ai_client = AIClient(model=settings.ai_model, api_key=None)
        self.agenda_service = AgendaService()

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
                if self.settings.use_ia:
                    summary = self.ai_client.generate_commercial_brief(vars_data)
                else:
                    summary = self.ai_client._deterministic_brief(vars_data)
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
            logger.info({"event": "action_end", "action": atype, "session_id": session_id})
        return state
