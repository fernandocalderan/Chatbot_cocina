from types import SimpleNamespace

from app.services.crm_service import CRMService


class FakeQuery:
    def __init__(self, items):
        self.items = items

    def filter(self, condition):
        target_id = str(condition.right.value)
        return FakeQuery([i for i in self.items if str(i.id) == target_id])

    def first(self):
        return self.items[0] if self.items else None


class FakeSession:
    def __init__(self):
        self.items = []

    def add(self, obj):
        if obj not in self.items:
            self.items.append(obj)

    def commit(self):
        return None

    def query(self, model):
        return FakeQuery([i for i in self.items if isinstance(i, model)])


def test_task_create_and_complete():
    session = FakeSession()
    svc = CRMService(session)
    task = svc.create_task("t1", {"title": "Llamar cliente", "owner_id": None})
    session.add(task)
    completed = svc.complete_task(str(task.id), user=SimpleNamespace(id="u1"))
    assert completed.status == "hecha"
