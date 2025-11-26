import types

from app.services.calendar.google_service import GoogleCalendarService
from app.services.calendar.microsoft_service import MicrosoftCalendarService


class DummyTenant(types.SimpleNamespace):
    pass


def test_google_create_event_stub():
    tenant = DummyTenant(
        id="t1", google_refresh_token="r1", google_calendar_connected=True
    )
    svc = GoogleCalendarService(tenant)
    res = svc.create_event(types.SimpleNamespace(slot_start=None))
    assert "success" in res


def test_microsoft_create_event_stub():
    tenant = DummyTenant(
        id="t1", microsoft_refresh_token="r1", microsoft_calendar_connected=True
    )
    svc = MicrosoftCalendarService(tenant)
    res = svc.create_event(types.SimpleNamespace(slot_start=None))
    assert "success" in res
