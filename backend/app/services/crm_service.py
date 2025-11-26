from __future__ import annotations

import time
from datetime import datetime
from typing import Any, Optional

from loguru import logger
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.leads import Lead
from app.models.task import Task


class CRMService:
    def __init__(self, db: Session):
        self.db = db

    def _log(self, payload: dict, level: str = "info"):
        log_func = getattr(logger, level, logger.info)
        log_func(payload)

    def _create_activity(
        self,
        tenant_id: str,
        lead_id: str,
        user_id: Optional[str],
        type_: str,
        content: str,
        meta: Optional[dict] = None,
    ):
        act = Activity(
            tenant_id=tenant_id,
            lead_id=lead_id,
            user_id=user_id,
            type=type_,
            content=content,
            meta=meta or {},
        )
        self.db.add(act)
        self.db.commit()
        return act

    def move_lead_to_stage(self, lead_id: str, new_status: str, user: Any, lost_reason: Optional[str] = None):
        start = time.perf_counter()
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            self._log({"lead_id": lead_id, "action": "move_stage", "success": False, "reason": "not_found"}, "warning")
            return None
        valid_status = {"nuevo", "contactado", "en_propuesta", "negociación", "ganado", "perdido"}
        if new_status not in valid_status:
            self._log({"lead_id": lead_id, "action": "move_stage", "success": False, "reason": "invalid_status"}, "warning")
            return None
        from_status = lead.status
        lead.status = new_status
        if new_status in {"ganado", "perdido"}:
            lead.closed_at = datetime.utcnow()
        if new_status == "perdido":
            lead.lost_reason = lost_reason
        self.db.add(lead)
        self.db.commit()
        self._create_activity(
            str(lead.tenant_id), str(lead.id), getattr(user, "id", None), "cambio_estado", f"{from_status}->{new_status}"
        )
        latency = (time.perf_counter() - start) * 1000
        self._log(
            {
                "tenant_id": str(lead.tenant_id),
                "user_id": str(getattr(user, "id", None)),
                "lead_id": str(lead.id),
                "action": "move_stage",
                "from_status": from_status,
                "to_status": new_status,
                "success": True,
                "latency_ms": round(latency, 2),
            }
        )
        return lead

    def assign_lead_owner(self, lead_id: str, user_id: str, current_user: Any = None):
        start = time.perf_counter()
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            self._log({"lead_id": lead_id, "action": "assign_owner", "success": False}, "warning")
            return None
        lead.owner_id = user_id
        self.db.add(lead)
        self.db.commit()
        self._create_activity(
            str(lead.tenant_id), str(lead.id), user_id, "cambio_estado", f"owner->{user_id}"
        )
        latency = (time.perf_counter() - start) * 1000
        self._log(
            {
                "tenant_id": str(lead.tenant_id),
                "user_id": user_id,
                "lead_id": str(lead.id),
                "action": "assign_owner",
                "from_status": None,
                "to_status": None,
                "success": True,
                "latency_ms": round(latency, 2),
            }
        )
        return lead

    def create_task(self, tenant_id: str, data: dict):
        start = time.perf_counter()
        task = Task(
            tenant_id=tenant_id,
            lead_id=data.get("lead_id"),
            owner_id=data.get("owner_id"),
            title=data["title"],
            description=data.get("description"),
            status=data.get("status", "pendiente"),
            due_date=data.get("due_date"),
            priority=data.get("priority", "media"),
        )
        self.db.add(task)
        self.db.commit()
        if task.lead_id:
            self._create_activity(
                tenant_id, str(task.lead_id), data.get("owner_id"), "nota", f"Tarea creada: {task.title}"
            )
        latency = (time.perf_counter() - start) * 1000
        self._log(
            {
                "tenant_id": tenant_id,
                "user_id": data.get("owner_id"),
                "lead_id": str(task.lead_id) if task.lead_id else None,
                "action": "create_task",
                "from_status": None,
                "to_status": None,
                "success": True,
                "latency_ms": round(latency, 2),
            }
        )
        return task

    def complete_task(self, task_id: str, user: Any):
        start = time.perf_counter()
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            self._log({"task_id": task_id, "action": "complete_task", "success": False}, "warning")
            return None
        task.status = "hecha"
        task.completed_at = datetime.utcnow()
        self.db.add(task)
        self.db.commit()
        if task.lead_id:
            self._create_activity(
                str(task.tenant_id),
                str(task.lead_id),
                getattr(user, "id", None),
                "nota",
                f"Tarea completada: {task.title}",
            )
        latency = (time.perf_counter() - start) * 1000
        self._log(
            {
                "tenant_id": str(task.tenant_id),
                "user_id": str(getattr(user, "id", None)),
                "lead_id": str(task.lead_id) if task.lead_id else None,
                "action": "complete_task",
                "from_status": None,
                "to_status": None,
                "success": True,
                "latency_ms": round(latency, 2),
            }
        )
        return task
