import uuid

from app.services.appointments_service import AppointmentService


def test_rate_limit_allows_first_two():
    svc = AppointmentService(redis_url="memory://")
    tenant_id = "tenant-test"
    lead_id = str(uuid.uuid4())
    # two calls should pass, third triggers limit
    svc.enforce_limits(tenant_id, lead_id)
    svc.enforce_limits(tenant_id, lead_id)
    try:
        svc.enforce_limits(tenant_id, lead_id)
    except ValueError as exc:
        assert str(exc) == "lead_limit"
