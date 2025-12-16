import threading
from typing import Any

from app.db.session import SessionLocal
from app.models.audits import AuditLog


class AuditService:
    """
    Registro de acciones administrativas.
    No debe romper el flujo principal ni propagar excepciones.
    """

    @staticmethod
    def _persist(payload: dict[str, Any]) -> None:
        db = SessionLocal()
        try:
            log = AuditLog(**payload)
            db.add(log)
            db.commit()
        except Exception:
            try:
                db.rollback()
            except Exception:
                pass
        finally:
            try:
                db.close()
            except Exception:
                pass

    @classmethod
    def log_admin_action(
        cls,
        actor: str | None,
        action: str,
        entity: str,
        entity_id: str | None = None,
        tenant_id: str | None = None,
        meta: dict | None = None,
    ) -> None:
        payload: dict[str, Any] = {
            "tenant_id": tenant_id,
            "entity": entity,
            "entity_id": entity_id or (tenant_id or "n/a"),
            "action": action,
            "actor": actor,
            "meta_data": meta or {},
        }
        # Ejecutar en thread separado para no bloquear.
        threading.Thread(target=cls._persist, args=(payload,), daemon=True).start()
