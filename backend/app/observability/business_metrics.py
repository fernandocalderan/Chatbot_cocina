from __future__ import annotations

import os
import threading
import time
from typing import Dict

from loguru import logger

try:
    from app.db.session import SessionLocal
    from app.models.leads import Lead
    from app.models.appointments import Appointment
except Exception:
    SessionLocal = None
    Lead = None
    Appointment = None


def compute_daily_metrics():
    if os.getenv("DISABLE_DB") == "1" or SessionLocal is None:
        logger.info({"event": "business_metrics_stub"})
        return {}
    db = SessionLocal()
    try:
        today_metrics: Dict[str, Dict[str, int]] = {}
        tenants = db.execute("SELECT id FROM tenants").fetchall()
        for (tenant_id,) in tenants:
            leads_total = (
                db.query(Lead).filter(Lead.tenant_id == tenant_id).count()
                if Lead
                else 0
            )
            leads_with_appt = (
                db.query(Lead)
                .filter(Lead.tenant_id == tenant_id, Lead.appointment_id.isnot(None))
                .count()
                if Lead and hasattr(Lead, "appointment_id")
                else 0
            )
            appts_total = (
                db.query(Appointment).filter(Appointment.tenant_id == tenant_id).count()
                if Appointment
                else 0
            )
            today_metrics[str(tenant_id)] = {
                "leads_total": leads_total,
                "leads_with_appointment": leads_with_appt,
                "appointments_total": appts_total,
            }
        logger.info({"event": "business_metrics_daily", "metrics": today_metrics})
        return today_metrics
    finally:
        db.close()


def start_business_metrics_loop():
    if os.getenv("PYTEST_CURRENT_TEST") or os.getenv("DISABLE_BUSINESS_METRICS") == "1":
        return

    def _loop():
        while True:
            time.sleep(24 * 60 * 60)
            try:
                compute_daily_metrics()
            except Exception as exc:
                logger.warning({"event": "business_metrics_error", "error": str(exc)})

    t = threading.Thread(target=_loop, daemon=True)
    t.start()
