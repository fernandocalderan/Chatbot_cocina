import logging
from typing import Any

from app.services.ai_client import AIClient

logger = logging.getLogger(__name__)


class ActionExecutor:
    def __init__(self, settings):
        self.settings = settings
        self.ai_client = AIClient(model=settings.ai_model, api_key=None)

    def execute_actions(self, actions: list[dict], session_id: str, state: dict, db=None):
        """
        Ejecuta stubs de acciones. Modifica el estado cuando aplica (p.ej. end_session).
        """
        for action in actions or []:
            atype = action.get("type")
            logger.info({"event": "action_start", "action": atype, "session_id": session_id, "params": action})
            if atype == "compute_lead_score":
                # Stub: scoring manejado en /chat/send
                pass
            elif atype == "create_or_update_lead":
                # Stub: ya manejado en /chat/send
                pass
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
                # Stub: nada aquí; slots se agregan en serialización del bloque
                pass
            elif atype == "end_session":
                state["ended"] = True
            logger.info({"event": "action_end", "action": atype, "session_id": session_id})
        return state
