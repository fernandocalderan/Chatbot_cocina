from datetime import datetime, timedelta
from typing import List, Optional


class AgendaService:
    """
    Agenda mínima: slots estáticos por días y horario fijo.
    """

    def __init__(self, days_ahead: int = 7):
        self.days_ahead = days_ahead
        self.daily_hours = [10, 11, 12, 16, 17]  # horario fijo

    def get_slots(self, tenant_id: Optional[str], visit_type: Optional[str], location: Optional[str]) -> List[str]:
        slots = []
        now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        for d in range(1, self.days_ahead + 1):
            day = now + timedelta(days=d)
            # Opcional: saltar domingos
            if day.weekday() == 6:
                continue
            for hour in self.daily_hours:
                slot = day.replace(hour=hour)
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
