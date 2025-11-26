from app.services.gdpr_service import GDPRService
from app.models.leads import Lead
from app.models.messages import Message


class FakeQuery:
    def __init__(self, items):
        self.items = items

    def filter(self, *args, **kwargs):
        return self

    def filter_by(self, **kwargs):
        return self

    def first(self):
        return self.items[0] if self.items else None

    def delete(self, synchronize_session=False):
        self.items.clear()
        return 0

    def all(self):
        return self.items

    def order_by(self, *args, **kwargs):
        return self


class FakeSession:
    def __init__(self):
        self.items = []

    def query(self, model):
        def match(item):
            try:
                return isinstance(item, model)
            except TypeError:
                return hasattr(item, "id")

        filtered = [i for i in self.items if match(i)]
        return FakeQuery(filtered)

    def add(self, obj):
        if obj not in self.items:
            self.items.append(obj)

    def commit(self):
        return None

    def rollback(self):
        return None


def test_forget_lead():
    db = FakeSession()
    lead = Lead(
        id="l1",
        tenant_id="t1",
        session_id="s1",
        meta_data={"contact_name": "Ana", "contact_email": "ana@x.com"},
    )
    msg = Message(
        id=1,
        tenant_id="t1",
        session_id="s1",
        role="user",
        content="hola",
        pii_version=1,
    )
    db.add(lead)
    db.add(msg)
    svc = GDPRService(db)
    ok = svc.forget_lead("t1", "l1")
    assert ok
    assert lead.meta_data.get("contact_name") != "Ana"


def test_purge_tenant():
    db = FakeSession()
    lead = Lead(id="l1", tenant_id="t1", session_id="s1", meta_data={}, pii_version=1)
    db.add(lead)
    svc = GDPRService(db)
    ok = svc.purge_tenant("t1")
    assert ok
