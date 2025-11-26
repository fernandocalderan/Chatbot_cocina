from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from loguru import logger
from sqlalchemy.orm import object_session

from app.workers.retry_queue import RetryQueue


class ReminderService:
    def __init__(self):
        self.retry_queue = RetryQueue.get_instance()

    def _mark_status(self, appointment: Any, status: str):
        try:
            appointment.reminder_status = status
            session = object_session(appointment)
            if session:
                session.add(appointment)
                session.commit()
        except Exception:
            # no bloquear flujo por errores de persistencia de recordatorios
            pass

    def _send_channels(self, appointment: Any, attempt: int = 0) -> bool:
        success_whatsapp = False
        success_email = False
        try:
            success_whatsapp = self.send_whatsapp_reminder(appointment)
        except Exception as exc:
            logger.warning(
                {
                    "tenant_id": str(getattr(appointment, "tenant_id", None)),
                    "lead_id": str(getattr(appointment, "lead_id", None)),
                    "appointment_id": str(getattr(appointment, "id", None)),
                    "action": "whatsapp_reminder",
                    "slot_start": getattr(appointment, "slot_start", None),
                    "timezone": getattr(
                        getattr(appointment, "slot_start", None), "tzinfo", None
                    ),
                    "source": "agenda_reminders",
                    "success": False,
                    "latency_ms": 0.0,
                    "error": str(exc),
                }
            )
        try:
            success_email = self.send_email_reminder(appointment)
        except Exception as exc:
            logger.warning(
                {
                    "tenant_id": str(getattr(appointment, "tenant_id", None)),
                    "lead_id": str(getattr(appointment, "lead_id", None)),
                    "appointment_id": str(getattr(appointment, "id", None)),
                    "action": "email_reminder",
                    "slot_start": getattr(appointment, "slot_start", None),
                    "timezone": getattr(
                        getattr(appointment, "slot_start", None), "tzinfo", None
                    ),
                    "source": "agenda_reminders",
                    "success": False,
                    "latency_ms": 0.0,
                    "error": str(exc),
                }
            )
        return success_whatsapp or success_email

    def _dispatch(self, appointment: Any, attempt: int = 0):
        if appointment is None or getattr(appointment, "slot_start", None) is None:
            return
        ok = self._send_channels(appointment, attempt=attempt)
        if ok:
            self._mark_status(appointment, "sent")
            return
        if attempt >= 2:
            self._mark_status(appointment, "failed")
            return
        self._mark_status(appointment, "retry_pending")
        self.retry_queue.schedule_retry(appointment, self._dispatch, attempt + 1)

    def schedule_reminders(self, appointment: Any):
        if appointment is None or getattr(appointment, "slot_start", None) is None:
            return
        slot_start = appointment.slot_start
        if slot_start.tzinfo is None:
            slot_start = slot_start.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        reminder_offsets = [timedelta(hours=24), timedelta(hours=2)]
        for offset in reminder_offsets:
            target_time = slot_start - offset
            delay_seconds = (target_time - now).total_seconds()
            if delay_seconds <= 0:
                # si la cita es inminente, enviar ya
                self.retry_queue.schedule_retry(
                    appointment, self._dispatch, attempt=0, delay_seconds=0
                )
            else:
                self.retry_queue.schedule_retry(
                    appointment, self._dispatch, attempt=0, delay_seconds=delay_seconds
                )

    def send_whatsapp_reminder(self, appointment: Any) -> bool:
        logger.info(
            {
                "tenant_id": str(getattr(appointment, "tenant_id", None)),
                "lead_id": str(getattr(appointment, "lead_id", None)),
                "appointment_id": str(getattr(appointment, "id", None)),
                "action": "whatsapp_reminder",
                "slot_start": getattr(appointment, "slot_start", None),
                "timezone": getattr(
                    getattr(appointment, "slot_start", None), "tzinfo", None
                ),
                "source": "agenda_reminders",
                "success": True,
                "latency_ms": 0.0,
            }
        )
        return True

    def send_email_reminder(self, appointment: Any) -> bool:
        logger.info(
            {
                "tenant_id": str(getattr(appointment, "tenant_id", None)),
                "lead_id": str(getattr(appointment, "lead_id", None)),
                "appointment_id": str(getattr(appointment, "id", None)),
                "action": "email_reminder",
                "slot_start": getattr(appointment, "slot_start", None),
                "timezone": getattr(
                    getattr(appointment, "slot_start", None), "tzinfo", None
                ),
                "source": "agenda_reminders",
                "success": True,
                "latency_ms": 0.0,
            }
        )
        return True
