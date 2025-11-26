from datetime import datetime

from app.services.agenda_service import AgendaService


def test_agenda_slots_respects_rules():
    now = datetime.utcnow()
    rules = {
        "days_ahead": 1,
        "slot_minutes": 30,
        "workdays": [now.weekday()],
        "opening_hours": {"start": "09:00", "end": "10:00"},
        "holidays": [],
        "timezone": "UTC",
    }
    svc = AgendaService(rules)
    slots = svc.get_slots(
        tenant_id=None, visit_type=None, location=None, rules_override=rules
    )
    assert isinstance(slots, list)
    assert all(slot.endswith("Z") for slot in slots)
