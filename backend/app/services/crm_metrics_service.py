from __future__ import annotations

import time
from datetime import datetime
from typing import Optional

from loguru import logger
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.leads import Lead
from app.models.task import Task


class CRMMetricsService:
    def __init__(self, db: Session):
        self.db = db

    def _log(self, payload: dict):
        logger.info(payload)

    def get_user_performance(self, tenant_id: str, user_id: str, date_from: Optional[datetime], date_to: Optional[datetime]):
        start = time.perf_counter()
        q = self.db.query(Lead).filter(Lead.tenant_id == tenant_id)
        if date_from:
            q = q.filter(Lead.created_at >= date_from)
        if date_to:
            q = q.filter(Lead.created_at <= date_to)
        assigned = q.filter(Lead.owner_id == user_id).count()
        won = q.filter(Lead.owner_id == user_id, Lead.status == "ganado").count()
        total_ops = q.filter(Lead.owner_id == user_id).count() or 1
        closed = (
            q.filter(Lead.owner_id == user_id, Lead.status.in_(["ganado", "perdido"]))
            .with_entities(func.avg(func.julianday(Lead.closed_at) - func.julianday(Lead.created_at)))
            .scalar()
        )
        tasks_done = (
            self.db.query(Task)
            .filter(Task.tenant_id == tenant_id, Task.owner_id == user_id, Task.status == "hecha")
            .count()
        )
        latency = (time.perf_counter() - start) * 1000
        self._log(
            {
                "tenant_id": tenant_id,
                "user_id": user_id,
                "lead_id": None,
                "action": "view_metrics",
                "from_status": None,
                "to_status": None,
                "success": True,
                "latency_ms": round(latency, 2),
            }
        )
        return {
            "assigned": assigned,
            "won": won,
            "win_rate": won / total_ops if total_ops else 0,
            "avg_time_to_close_days": float(closed or 0),
            "tasks_completed": tasks_done,
        }

    def get_tenant_funnel(self, tenant_id: str, date_from: Optional[datetime], date_to: Optional[datetime]):
        start = time.perf_counter()
        q = self.db.query(Lead).filter(Lead.tenant_id == tenant_id)
        if date_from:
            q = q.filter(Lead.created_at >= date_from)
        if date_to:
            q = q.filter(Lead.created_at <= date_to)
        statuses = ["nuevo", "contactado", "en_propuesta", "negociación", "ganado", "perdido"]
        counts = {s: q.filter(Lead.status == s).count() for s in statuses}
        total = sum(counts.values()) or 1
        conversion = {
            "nuevo_contactado": counts.get("contactado", 0) / counts.get("nuevo", 1),
            "contactado_en_propuesta": counts.get("en_propuesta", 0) / counts.get("contactado", 1),
            "en_propuesta_negociacion": counts.get("negociación", 0) / counts.get("en_propuesta", 1),
            "negociacion_ganado": counts.get("ganado", 0) / counts.get("negociación", 1),
        }
        latency = (time.perf_counter() - start) * 1000
        self._log(
            {
                "tenant_id": tenant_id,
                "user_id": None,
                "lead_id": None,
                "action": "view_metrics",
                "from_status": None,
                "to_status": None,
                "success": True,
                "latency_ms": round(latency, 2),
            }
        )
        return {"counts": counts, "conversion": conversion, "total": total}
