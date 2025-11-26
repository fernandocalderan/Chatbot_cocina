from types import SimpleNamespace

from app.models.leads import Lead
from app.services.crm_service import CRMService


class FakeQuery:
    def __init__(self, items):
        self.items = items

    def filter(self, condition):
        # simple id equality check
        target_id = str(condition.right.value)
        return FakeQuery([i for i in self.items if str(i.id) == target_id])

    def first(self):
        return self.items[0] if self.items else None

    def count(self):
        return len(self.items)


class FakeSession:
    def __init__(self):
        self.items = []

    def add(self, obj):
        if obj not in self.items:
            self.items.append(obj)

    def commit(self):
        return None

    def query(self, model):
        filtered = [i for i in self.items if isinstance(i, model)]
        return FakeQuery(filtered)


def test_lead_move_flow():
    session = FakeSession()
    lead = Lead(tenant_id="t1", status="nuevo")
    session.add(lead)
    svc = CRMService(session)
    svc.move_lead_to_stage(str(lead.id), "contactado", user=SimpleNamespace(id="u1"))
    svc.move_lead_to_stage(str(lead.id), "ganado", user=SimpleNamespace(id="u1"))
    updated = session.query(Lead).first()
    assert updated.status == "ganado"
