from datetime import datetime, timedelta, time, date
from typing import List, Optional

DEFAULT_RULES = {
    "days_ahead": 7,
    "slot_minutes": 30,
    "workdays": [0, 1, 2, 3, 4],  # 0=Monday
    "daily_ranges": [
        {"start": "10:00", "end": "14:00"},
        {"start": "16:00", "end": "19:00"},
    ],
    "holidays": [],
}


def _parse_time(hhmm: str) -> time:
    parts = hhmm.split(":")
    return time(int(parts[0]), int(parts[1]))


class AgendaService:
    """
    Agenda configurable por tenant: horarios, festivos y duración de slot.
    """

    def __init__(self, rules: dict | None = None):
        self.rules = rules or DEFAULT_RULES

    def _generate_slots_for_day(self, day: datetime, slot_minutes: int, ranges: list[dict]) -> list[datetime]:
        slots: list[datetime] = []
        for r in ranges:
            start_t = _parse_time(r["start"])
            end_t = _parse_time(r["end"])
            cur = day.replace(hour=start_t.hour, minute=start_t.minute, second=0, microsecond=0)
            end_dt = day.replace(hour=end_t.hour, minute=end_t.minute, second=0, microsecond=0)
            while cur + timedelta(minutes=slot_minutes) <= end_dt:
                slots.append(cur)
                cur += timedelta(minutes=slot_minutes)
        return slots

    def get_slots(
        self, tenant_id: Optional[str], visit_type: Optional[str], location: Optional[str], rules_override: dict | None = None
    ) -> List[str]:
        rules = rules_override or self.rules
        days_ahead = rules.get("days_ahead", DEFAULT_RULES["days_ahead"])
        slot_minutes = rules.get("slot_minutes", DEFAULT_RULES["slot_minutes"])
        workdays = rules.get("workdays", DEFAULT_RULES["workdays"])
        ranges = rules.get("daily_ranges", DEFAULT_RULES["daily_ranges"])
        holidays = {date.fromisoformat(h) for h in rules.get("holidays", []) if h}

        slots: list[str] = []
        now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        for d in range(1, days_ahead + 1):
            day = now + timedelta(days=d)
            if day.weekday() not in workdays:
                continue
            if day.date() in holidays:
                continue
            day_slots = self._generate_slots_for_day(day, slot_minutes, ranges)
            for slot in day_slots:
                if slot > now:
                    slots.append(slot.isoformat() + "Z")
        return slots

    def book(self, db, lead_id, tenant_id, slot_start: datetime, slot_end: datetime, visit_type: Optional[str]):
        from app.models.appointments import Appointment
        from sqlalchemy.exc import SQLAlchemyError

        try:
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
            return appt
        except SQLAlchemyError:
            db.rollback()
            return None
