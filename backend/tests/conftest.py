import os
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Any, List

# Ensure the backend root is on sys.path so `import app` works when running tests from anywhere
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# For tests, default to DISABLE_DB to avoid hitting real Postgres
os.environ.setdefault("DISABLE_DB", "1")

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_db
from app.core.config import get_settings
from app.main import app
from app.models.appointments import Appointment
from app.models.flows import Flow as FlowVersioned
from app.models.leads import Lead
from app.models.messages import Message
from app.models.sessions import Session
from app.models.users import User


@pytest.fixture(autouse=True)
def force_disable_db(monkeypatch):
    monkeypatch.setenv("DISABLE_DB", "1")
    yield


@pytest.fixture(autouse=True)
def fake_sessionlocal(monkeypatch):
    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def filter_by(self, **kwargs):
            return self

        def first(self):
            return None

        def all(self):
            return []

        def count(self):
            return 0

        def offset(self, *args, **kwargs):
            return self

        def limit(self, *args, **kwargs):
            return self

        def order_by(self, *args, **kwargs):
            return self

    class FakeSession:
        def query(self, *args, **kwargs):
            return FakeQuery()

        def add(self, *args, **kwargs):
            return None

        def add_all(self, *args, **kwargs):
            return None

        def commit(self):
            return None

        def rollback(self):
            return None

        def flush(self):
            return None

        def close(self):
            return None

    fake_factory = lambda: FakeSession()
    monkeypatch.setattr("app.db.session.SessionLocal", fake_factory, raising=False)
    monkeypatch.setattr("app.api.deps.SessionLocal", fake_factory, raising=False)
    monkeypatch.setattr("app.middleware.tenant_resolver.SessionLocal", fake_factory, raising=False)

    # Override get_db to yield the fake session
    def _fake_get_db():
        sess = FakeSession()
        try:
            yield sess
        finally:
            sess.close()

    monkeypatch.setattr("app.api.deps.get_db", _fake_get_db, raising=False)
    yield


@pytest.fixture(autouse=True)
def force_password_ok(monkeypatch):
    def always_true(p, h):
        return True

    monkeypatch.setattr("app.core.security.verify_password", always_true)
    monkeypatch.setattr("app.api.auth.verify_password", always_true)
    yield


class QueryStub:
    def __init__(self, data: List[Any]):
        self.data = list(data)
        self._offset = 0
        self._limit = None

    def _apply_condition(self, cond):
        left_key = getattr(getattr(cond, "left", None), "key", None)
        right = getattr(cond, "right", None)
        right_val = getattr(right, "value", right)
        if left_key is None:
            return
        self.data = [row for row in self.data if getattr(row, left_key, None) == right_val]

    def filter(self, *conditions):
        for cond in conditions:
            self._apply_condition(cond)
        return self

    def filter_by(self, **kwargs):
        for key, value in kwargs.items():
            self.data = [row for row in self.data if getattr(row, key, None) == value]
        return self

    def order_by(self, *args, **kwargs):
        return self

    def offset(self, offset: int):
        self._offset = offset
        return self

    def limit(self, limit: int):
        self._limit = limit
        return self

    def count(self):
        return len(self.data)

    def first(self):
        return (self.data + [None])[0]

    def all(self):
        end = None if self._limit is None else self._offset + self._limit
        return self.data[self._offset : end]


class DBStub:
    def __init__(self, datasets: dict[type, list[Any]]):
        self.datasets = datasets

    def query(self, model):
        return QueryStub(self.datasets.get(model, []))

    def add(self, *args, **kwargs):
        return None

    def commit(self):
        return None

    def rollback(self):
        return None

    def close(self):
        return None


@pytest.fixture
def demo_data():
    tenant_id = "tenant-demo"
    other_tenant = "tenant-other"
    user = User(id="user-demo", tenant_id=tenant_id, email="demo@example.com", hashed_password="stub")
    session = Session(
        id="session-demo",
        tenant_id=tenant_id,
        external_user_id=None,
        canal="web",
        idioma_detectado="es",
        state="ask_type",
        last_block_id="ask_type",
        variables_json={"project_type": "kitchen"},
        expires_at=datetime.now(timezone.utc) + timedelta(hours=2),
        created_at=datetime.now(timezone.utc) - timedelta(hours=1),
        updated_at=datetime.now(timezone.utc),
    )
    leads = [
        Lead(
            id="lead-demo",
            tenant_id=tenant_id,
            session_id=session.id,
            status="hot",
            score=90,
            score_breakdown_json={"budget": {"score": 90, "weight": 50}},
            meta_data={"contact_name": "Ana Demo", "project_type": "kitchen"},
            created_at=datetime.now(timezone.utc) - timedelta(days=1),
        ),
        Lead(
            id="lead-other",
            tenant_id=other_tenant,
            session_id="session-other",
            status="warm",
            score=40,
            score_breakdown_json={},
            meta_data={"contact_name": "Otro"},
            created_at=datetime.now(timezone.utc) - timedelta(hours=3),
        ),
    ]
    appointments = [
        Appointment(
            id="appt-demo",
            tenant_id=tenant_id,
            lead_id=leads[0].id,
            slot_start=datetime.now(timezone.utc) + timedelta(days=1),
            slot_end=datetime.now(timezone.utc) + timedelta(days=1, minutes=30),
            origen="demo",
            estado="booked",
            notas=None,
        ),
        Appointment(
            id="appt-other",
            tenant_id=other_tenant,
            lead_id=leads[1].id,
            slot_start=datetime.now(timezone.utc) + timedelta(days=2),
            slot_end=datetime.now(timezone.utc) + timedelta(days=2, minutes=30),
            origen="demo",
            estado="booked",
            notas=None,
        ),
    ]
    flows = [
        FlowVersioned(
            id="flow-demo",
            tenant_id=tenant_id,
            version=2,
            schema_json={"blocks": {"welcome": {"type": "message"}}, "version": 2},
            estado="published",
            published_at=datetime.now(timezone.utc),
        ),
        FlowVersioned(
            id="flow-other",
            tenant_id=other_tenant,
            version=1,
            schema_json={"blocks": {}, "version": 1},
            estado="published",
            published_at=datetime.now(timezone.utc),
        ),
    ]
    messages = [
        Message(
            id=1,
            tenant_id=tenant_id,
            session_id=session.id,
            role="assistant",
            content="Hola",
            block_id="welcome",
            ai_meta={},
            attachments=[],
            created_at=datetime.now(timezone.utc) - timedelta(minutes=10),
        ),
        Message(
            id=2,
            tenant_id=other_tenant,
            session_id="session-other",
            role="assistant",
            content="No debería verse",
            block_id="welcome",
            ai_meta={},
            attachments=[],
            created_at=datetime.now(timezone.utc) - timedelta(minutes=5),
        ),
    ]
    return {
        "tenant_id": tenant_id,
        "user": user,
        "session": session,
        "leads": leads,
        "appointments": appointments,
        "flows": flows,
        "messages": messages,
    }


@pytest.fixture
def client_demo(monkeypatch, demo_data):
    settings = get_settings()
    prev_db_env = os.environ.get("DISABLE_DB")
    os.environ["DISABLE_DB"] = "1"
    settings.jwt_secret = "demo-secret"
    settings.panel_api_token = None

    db_stub = DBStub(
        {
            User: [demo_data["user"]],
            Lead: demo_data["leads"],
            Appointment: demo_data["appointments"],
            FlowVersioned: demo_data["flows"],
            Session: [demo_data["session"]],
            Message: demo_data["messages"],
        }
    )

    def override_get_db():
        try:
            yield db_stub
        finally:
            db_stub.close()

    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr("app.core.security.verify_password", lambda password, hashed: True)
    monkeypatch.setattr("app.api.auth.verify_password", lambda password, hashed: True, raising=False)

    yield TestClient(app)

    app.dependency_overrides.clear()
    if prev_db_env is None:
        os.environ.pop("DISABLE_DB", None)
    else:
        os.environ["DISABLE_DB"] = prev_db_env


@pytest.fixture
def demo_headers(client_demo, demo_data):
    resp = client_demo.post(
        "/v1/auth/login",
        json={"email": demo_data["user"].email, "password": "secret"},
        headers={"X-Tenant-ID": demo_data["tenant_id"]},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}", "X-Tenant-ID": demo_data["tenant_id"]}
