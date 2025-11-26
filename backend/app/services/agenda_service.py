from datetime import date, datetime, time, timedelta, timezone
from typing import List, Optional

from loguru import logger
from zoneinfo import ZoneInfo

from app.db.session import SessionLocal
from app.models.appointments import Appointment
from app.models.configs import Config
from app.models.tenants import Tenant
from app.services.calendar.google_service import GoogleCalendarService
from app.services.calendar.microsoft_service import MicrosoftCalendarService

DEFAULT_RULES = {
    "days_ahead": 7,
    "slot_minutes": 30,
    "workdays": [0, 1, 2, 3, 4],  # 0=Monday
    "opening_hours": {"start": "10:00", "end": "19:00"},
    "holidays": [],
    "timezone": "UTC",
}


def _parse_time(hhmm: str) -> time:
    parts = hhmm.split(":")
    return time(int(parts[0]), int(parts[1]))


class AgendaService:
    """
    Agenda configurable por tenant: horarios, festivos y duración de slot.
    """

    def __init__(self, rules: dict | None = None, db=None):
        self.rules = rules or DEFAULT_RULES
        self.db = db

    def _generate_slots_for_day(
        self, day: datetime, slot_minutes: int, ranges: list[dict]
    ) -> list[datetime]:
        slots: list[datetime] = []
        for r in ranges:
            start_t = _parse_time(r["start"])
            end_t = _parse_time(r["end"])
            cur = day.replace(
                hour=start_t.hour, minute=start_t.minute, second=0, microsecond=0
            )
            end_dt = day.replace(
                hour=end_t.hour, minute=end_t.minute, second=0, microsecond=0
            )
            while cur + timedelta(minutes=slot_minutes) <= end_dt:
                slots.append(cur)
                cur += timedelta(minutes=slot_minutes)
        return slots

    def _resolve_ranges(self, rules: dict) -> list[dict]:
        if "opening_hours" in rules and isinstance(rules.get("opening_hours"), dict):
            oh = rules["opening_hours"]
            start_val = oh.get("start")
            end_val = oh.get("end")
            if start_val and end_val:
                return [{"start": start_val, "end": end_val}]
        if "daily_ranges" in rules and isinstance(rules.get("daily_ranges"), list):
            return rules["daily_ranges"]
        return [
            {"start": "10:00", "end": "14:00"},
            {"start": "16:00", "end": "19:00"},
        ]

    def _load_rules(
        self, tenant_id: Optional[str], rules_override: Optional[dict]
    ) -> tuple[dict, Optional[Tenant], list]:
        rules = dict(DEFAULT_RULES)
        holidays: list[str] = []
        session = self.db or SessionLocal()
        close_session = self.db is None
        tenant = None
        try:
            if tenant_id:
                tenant = session.query(Tenant).filter(Tenant.id == tenant_id).first()
            cfg = (
                session.query(Config)
                .filter(Config.tenant_id == tenant_id, Config.tipo == "agenda_rules")
                .order_by(Config.version.desc())
                .first()
                if tenant_id
                else None
            )
            payload = cfg.payload_json if cfg else {}
            source_rules = rules_override or payload or {}
            if tenant:
                if tenant.workdays:
                    rules["workdays"] = tenant.workdays
                if tenant.opening_hours:
                    rules["opening_hours"] = tenant.opening_hours
                if tenant.slot_duration:
                    rules["slot_minutes"] = tenant.slot_duration
                if tenant.timezone:
                    rules["timezone"] = tenant.timezone
            for key in (
                "workdays",
                "opening_hours",
                "slot_minutes",
                "slot_duration",
                "timezone",
                "holidays",
                "days_ahead",
            ):
                if source_rules.get(key) is not None:
                    if key == "slot_duration":
                        rules["slot_minutes"] = source_rules.get(key)
                    else:
                        rules[key] = source_rules.get(key)
            holidays = source_rules.get("holidays", [])
        finally:
            if close_session:
                session.close()
        return rules, tenant, holidays

    def _load_existing_appointments(
        self, tenant_id: Optional[str], start: datetime, end: datetime, session
    ) -> list[Appointment]:
        if not tenant_id:
            return []
        return (
            session.query(Appointment)
            .filter(
                Appointment.tenant_id == tenant_id,
                Appointment.slot_start < end,
                Appointment.slot_end > start,
            )
            .all()
        )

    def get_slots(
        self,
        tenant_id: Optional[str],
        visit_type: Optional[str],
        location: Optional[str],
        rules_override: dict | None = None,
        db=None,
    ) -> List[str]:
        import time as _time

        session = db or self.db or SessionLocal()
        close_session = db is None and self.db is None
        start_time = _time.perf_counter()
        try:
            rules, tenant, holidays_raw = self._load_rules(tenant_id, rules_override)
            days_ahead = rules.get("days_ahead", DEFAULT_RULES["days_ahead"])
            slot_minutes = rules.get("slot_minutes", DEFAULT_RULES["slot_minutes"])
            workdays = rules.get("workdays", DEFAULT_RULES["workdays"])
            ranges = self._resolve_ranges(rules)
            holidays = {date.fromisoformat(h) for h in holidays_raw or [] if h}
            tz_name = rules.get("timezone") or DEFAULT_RULES.get("timezone") or "UTC"
            try:
                tzinfo = ZoneInfo(tz_name)
            except Exception:
                tzinfo = timezone.utc

            slots: list[str] = []
            now = datetime.now(tz=tzinfo).replace(second=0, microsecond=0)
            period_end = now + timedelta(days=days_ahead + 1)
            existing = self._load_existing_appointments(
                tenant_id, now, period_end, session
            )
            external_events: list[tuple[datetime, datetime]] = []
            if tenant and getattr(tenant, "google_calendar_connected", False):
                gs = GoogleCalendarService(tenant)
                events_resp = gs.list_events(now.isoformat(), period_end.isoformat())
                for ev in events_resp.get("events", []):
                    try:
                        start_at = ev.get("start")
                        end_at = ev.get("end")
                        if start_at and end_at:
                            external_events.append(
                                (
                                    datetime.fromisoformat(start_at),
                                    datetime.fromisoformat(end_at),
                                )
                            )
                    except Exception:
                        continue
            if tenant and getattr(tenant, "microsoft_calendar_connected", False):
                ms = MicrosoftCalendarService(tenant)
                events_resp = ms.list_events(now.isoformat(), period_end.isoformat())
                for ev in events_resp.get("events", []):
                    try:
                        start_at = ev.get("start")
                        end_at = ev.get("end")
                        if start_at and end_at:
                            external_events.append(
                                (
                                    datetime.fromisoformat(start_at),
                                    datetime.fromisoformat(end_at),
                                )
                            )
                    except Exception:
                        continue

            for d in range(1, days_ahead + 1):
                day = now + timedelta(days=d)
                if day.weekday() not in workdays:
                    continue
                if day.date() in holidays:
                    continue
                day_slots = self._generate_slots_for_day(day, slot_minutes, ranges)
                for slot in day_slots:
                    if slot <= now:
                        continue
                    slot_end = slot + timedelta(minutes=slot_minutes)
                    slot_utc_start = slot.astimezone(timezone.utc)
                    slot_utc_end = slot_end.astimezone(timezone.utc)
                    overlap = any(
                        appt.slot_start < slot_utc_end
                        and appt.slot_end > slot_utc_start
                        for appt in existing
                    )
                    overlap_ext = any(
                        ext_start < slot_utc_end and ext_end > slot_utc_start
                        for ext_start, ext_end in external_events
                    )
                    if not overlap and not overlap_ext:
                        slots.append(
                            slot.astimezone(timezone.utc)
                            .isoformat()
                            .replace("+00:00", "Z")
                        )

            latency_ms = (_time.perf_counter() - start_time) * 1000
            logger.info(
                {
                    "tenant_id": tenant_id,
                    "lead_id": None,
                    "appointment_id": None,
                    "action": "list_slots",
                    "slot_start": None,
                    "timezone": getattr(tenant, "timezone", None)
                    or rules.get("timezone"),
                    "source": "agenda_service",
                    "success": True,
                    "latency_ms": round(latency_ms, 2),
                }
            )
            return slots
        finally:
            if close_session:
                session.close()

    def book(
        self,
        db,
        lead_id,
        tenant_id,
        slot_start: datetime,
        slot_end: datetime,
        visit_type: Optional[str],
    ):
        import time as _time
        from sqlalchemy.exc import SQLAlchemyError

        start_time = _time.perf_counter()
        try:
            try:
                from app.services.appointments_service import AppointmentService

                AppointmentService().enforce_limits(
                    tenant_id, str(lead_id) if lead_id else None
                )
            except ValueError as limit_exc:
                logger.warning(
                    {
                        "tenant_id": tenant_id,
                        "lead_id": str(lead_id) if lead_id else None,
                        "appointment_id": None,
                        "action": "book",
                        "slot_start": slot_start.isoformat(),
                        "timezone": (
                            slot_start.tzinfo.tzname(None)
                            if slot_start.tzinfo
                            else None
                        ),
                        "source": "agenda_service",
                        "success": False,
                        "latency_ms": 0.0,
                        "fallback": str(limit_exc),
                    }
                )
                return None
            appt = Appointment(
                tenant_id=tenant_id,
                lead_id=lead_id,
                slot_start=slot_start,
                slot_end=slot_end,
                estado="booked",
                origen="chat",
                notas=None,
                reminder_status=None,
            )
            db.add(appt)
            db.commit()
            db.refresh(appt)
            try:
                from app.services.agenda_reminders import ReminderService

                ReminderService().schedule_reminders(appt)
            except Exception as reminder_exc:
                logger.warning(
                    {"event": "reminder_schedule_failed", "error": str(reminder_exc)}
                )
            latency_ms = (_time.perf_counter() - start_time) * 1000
            logger.info(
                {
                    "tenant_id": tenant_id,
                    "lead_id": str(lead_id) if lead_id else None,
                    "appointment_id": str(appt.id),
                    "action": "book",
                    "slot_start": slot_start.isoformat(),
                    "timezone": (
                        slot_start.tzinfo.tzname(None) if slot_start.tzinfo else None
                    ),
                    "source": "agenda_service",
                    "success": True,
                    "latency_ms": round(latency_ms, 2),
                }
            )
            return appt
        except SQLAlchemyError:
            db.rollback()
            latency_ms = (_time.perf_counter() - start_time) * 1000
            logger.error(
                {
                    "tenant_id": tenant_id,
                    "lead_id": str(lead_id) if lead_id else None,
                    "appointment_id": None,
                    "action": "book",
                    "slot_start": slot_start.isoformat(),
                    "timezone": (
                        slot_start.tzinfo.tzname(None) if slot_start.tzinfo else None
                    ),
                    "source": "agenda_service",
                    "success": False,
                    "latency_ms": round(latency_ms, 2),
                }
            )
            return None
