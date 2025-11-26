from __future__ import annotations

from typing import Optional

import redis
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.appointments import Appointment
from app.services.agenda_reminders import ReminderService


class AppointmentService:
    def __init__(self, redis_url: Optional[str] = None):
        self.settings = get_settings()
        self.redis_url = redis_url or self.settings.redis_url
        try:
            self.redis = redis.from_url(self.redis_url)
        except Exception:
            self.redis = None
        self.reminders = ReminderService()

    def _incr(self, key: str, ttl_seconds: int) -> int:
        if not self.redis:
            return 1
        pipe = self.redis.pipeline()
        pipe.incr(key, 1)
        pipe.expire(key, ttl_seconds)
        count, _ = pipe.execute()
        return int(count)

    def enforce_limits(self, tenant_id: str, lead_id: Optional[str]):
        tenant_count = self._incr(f"tenant:{tenant_id}:appointments_daily", 86_400)
        if tenant_count > 20:
            raise ValueError("tenant_limit")
        if lead_id:
            lead_count = self._incr(f"lead:{lead_id}:appointments_daily", 86_400)
            if lead_count > 2:
                raise ValueError("lead_limit")

    def cancel_appointment(
        self, db: Session, appointment_id: str, tenant_id: str
    ) -> Optional[Appointment]:
        appt = (
            db.query(Appointment)
            .filter(
                Appointment.id == appointment_id, Appointment.tenant_id == tenant_id
            )
            .first()
        )
        if not appt:
            return None
        try:
            appt.estado = "cancelled"
            appt.reminder_status = "cancelled"
            db.add(appt)
            db.commit()
            db.refresh(appt)
            logger.info(
                {
                    "tenant_id": tenant_id,
                    "lead_id": str(appt.lead_id) if appt.lead_id else None,
                    "appointment_id": str(appt.id),
                    "action": "cancel",
                    "slot_start": (
                        appt.slot_start.isoformat() if appt.slot_start else None
                    ),
                    "timezone": (
                        appt.slot_start.tzinfo.tzname(None)
                        if appt.slot_start and appt.slot_start.tzinfo
                        else None
                    ),
                    "source": "appointments_service",
                    "success": True,
                    "latency_ms": 0.0,
                }
            )
            return appt
        except SQLAlchemyError:
            db.rollback()
            logger.error(
                {
                    "tenant_id": tenant_id,
                    "lead_id": str(appt.lead_id) if appt and appt.lead_id else None,
                    "appointment_id": str(appt.id) if appt else None,
                    "action": "cancel",
                    "slot_start": (
                        appt.slot_start.isoformat()
                        if appt and appt.slot_start
                        else None
                    ),
                    "timezone": (
                        appt.slot_start.tzinfo.tzname(None)
                        if appt and appt.slot_start and appt.slot_start.tzinfo
                        else None
                    ),
                    "source": "appointments_service",
                    "success": False,
                    "latency_ms": 0.0,
                }
            )
            return None

    def reschedule_appointment(
        self,
        db: Session,
        appointment_id: str,
        tenant_id: str,
        new_slot_start,
        new_slot_end,
    ) -> Optional[Appointment]:
        appt = (
            db.query(Appointment)
            .filter(
                Appointment.id == appointment_id, Appointment.tenant_id == tenant_id
            )
            .first()
        )
        if not appt:
            return None
        try:
            overlap = (
                db.query(Appointment)
                .filter(
                    Appointment.tenant_id == tenant_id,
                    Appointment.id != appointment_id,
                    Appointment.slot_start < new_slot_end,
                    Appointment.slot_end > new_slot_start,
                )
                .first()
            )
            if overlap:
                raise ValueError("slot_unavailable")

            appt.slot_start = new_slot_start
            appt.slot_end = new_slot_end
            appt.estado = "booked"
            appt.reminder_status = None
            db.add(appt)
            db.commit()
            db.refresh(appt)
            self.reminders.schedule_reminders(appt)
            logger.info(
                {
                    "tenant_id": tenant_id,
                    "lead_id": str(appt.lead_id) if appt.lead_id else None,
                    "appointment_id": str(appt.id),
                    "action": "reschedule",
                    "slot_start": (
                        appt.slot_start.isoformat() if appt.slot_start else None
                    ),
                    "timezone": (
                        appt.slot_start.tzinfo.tzname(None)
                        if appt.slot_start and appt.slot_start.tzinfo
                        else None
                    ),
                    "source": "appointments_service",
                    "success": True,
                    "latency_ms": 0.0,
                }
            )
            return appt
        except ValueError:
            db.rollback()
            return None
        except SQLAlchemyError:
            db.rollback()
            logger.error(
                {
                    "tenant_id": tenant_id,
                    "lead_id": str(appt.lead_id) if appt and appt.lead_id else None,
                    "appointment_id": str(appt.id) if appt else None,
                    "action": "reschedule",
                    "slot_start": (
                        appt.slot_start.isoformat()
                        if appt and appt.slot_start
                        else None
                    ),
                    "timezone": (
                        appt.slot_start.tzinfo.tzname(None)
                        if appt and appt.slot_start and appt.slot_start.tzinfo
                        else None
                    ),
                    "source": "appointments_service",
                    "success": False,
                    "latency_ms": 0.0,
                }
            )
            return None
