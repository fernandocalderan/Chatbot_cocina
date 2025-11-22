import logging
from typing import Any

logger = logging.getLogger(__name__)


class ActionExecutor:
    def __init__(self):
        pass

    def execute_actions(self, actions: list[dict], session_id: str, state: dict, db=None):
        """
        Ejecuta stubs de acciones. Modifica el estado cuando aplica (p.ej. end_session).
        """
        for action in actions or []:
            atype = action.get("type")
            logger.info({"event": "action_start", "action": atype, "session_id": session_id, "params": action})
            if atype == "compute_lead_score":
                # Stub: no hace nada, scoring ya se maneja en /chat/send
                pass
            elif atype == "create_or_update_lead":
                # Stub: ya manejado en /chat/send
                pass
            elif atype == "generate_ai_summary":
                # Stub: no genera IA aún
                state.setdefault("vars", {})["ai_summary"] = "Resumen IA pendiente (stub)."
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
