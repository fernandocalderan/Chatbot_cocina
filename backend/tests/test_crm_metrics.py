from datetime import datetime, timedelta, timezone

from app.models.leads import Lead
from app.models.task import Task
from app.services.crm_metrics_service import CRMMetricsService


class FakeQuery:
    def __init__(self, items):
        self.items = items

    def filter(self, *args, **kwargs):
        return self

    def count(self):
        return len(self.items)

    def with_entities(self, *args, **kwargs):
        return self

    def scalar(self):
        return 1

    def all(self):
        return self.items


class FakeSession:
    def __init__(self, leads, tasks):
        self._leads = leads
        self._tasks = tasks

    def query(self, model):
        if model == Lead:
            return FakeQuery(self._leads)
        if model == Task:
            return FakeQuery(self._tasks)
        return FakeQuery([])


def test_metrics_user_and_funnel():
    now = datetime.now(timezone.utc)
    lead1 = Lead(
        tenant_id="t1",
        owner_id="u1",
        status="ganado",
        created_at=now - timedelta(days=2),
        closed_at=now,
    )
    lead2 = Lead(
        tenant_id="t1",
        owner_id="u1",
        status="contactado",
        created_at=now - timedelta(days=1),
    )
    task = Task(tenant_id="t1", owner_id="u1", title="Follow up", status="hecha")
    session = FakeSession([lead1, lead2], [task])
    svc = CRMMetricsService(session)
    perf = svc.get_user_performance("t1", "u1", None, None)
    funnel = svc.get_tenant_funnel("t1", None, None)
    assert perf["assigned"] >= 2
    assert "nuevo" in funnel["counts"]
