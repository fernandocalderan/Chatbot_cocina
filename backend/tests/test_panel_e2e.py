import os
from datetime import datetime, timedelta, timezone
from typing import Any, List

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


class QueryStub:
    def __init__(self, data: List[Any]):
        self.data = list(data)
        self._offset = 0
        self._limit = None

    def filter(self, *args, **kwargs):
        # Filters are ignored; dataset already scoped for the tenant in the stub.
        return self

    def filter_by(self, **kwargs):
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


@pytest.fixture(scope="module", autouse=True)
def settings_patch():
    os.environ["DISABLE_DB"] = "1"  # middleware usará el header X-Tenant-ID
    settings = get_settings()
    settings.jwt_secret = "e2e-secret"
    settings.panel_api_token = None
    yield
    os.environ.pop("DISABLE_DB", None)


@pytest.fixture
def force_password_ok(monkeypatch):
    import app.core.security
    import app.api.auth

    monkeypatch.setattr("app.core.security.verify_password", lambda plain, hashed: True)
    monkeypatch.setattr("app.api.auth.verify_password", lambda plain, hashed: True, raising=False)


@pytest.fixture
def test_client(monkeypatch, force_password_ok):
    tenant_id = "tenant-e2e"
    user = User(id="user-e2e", tenant_id=tenant_id, email="user@example.com", hashed_password="stub")
    session_id = "session-e2e"
    session = Session(
        id=session_id,
        tenant_id=tenant_id,
        external_user_id=None,
        canal="web",
        idioma_detectado="es",
        state="ask_type",
        last_block_id="ask_type",
        variables_json={"project_type": "kitchen"},
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    leads = [
        Lead(
            id="lead-e2e",
            tenant_id=tenant_id,
            session_id=session_id,
            status="hot",
            score=90,
            score_breakdown_json={"budget": {"score": 90, "weight": 50}},
            meta_data={"contact_name": "Ana", "contact_phone": "+34123123123", "project_type": "kitchen"},
            created_at=datetime.now(timezone.utc) - timedelta(days=1),
        )
    ]
    appts = [
        Appointment(
            id="appt-e2e",
            tenant_id=tenant_id,
            lead_id=leads[0].id,
            slot_start=datetime.now(timezone.utc) + timedelta(days=1),
            slot_end=datetime.now(timezone.utc) + timedelta(days=1, minutes=30),
            origen="demo",
            estado="booked",
            notas=None,
        )
    ]
    flow = FlowVersioned(
        id="flow-e2e",
        tenant_id=tenant_id,
        version=2,
        schema_json={"blocks": {}, "version": 2},
        estado="published",
        published_at=datetime.now(timezone.utc),
    )
    messages = [
        Message(
            id=1,
            tenant_id=tenant_id,
            session_id=session_id,
            role="assistant",
            content="Hola",
            block_id="welcome",
            ai_meta={},
            attachments=[],
            created_at=datetime.now(timezone.utc) - timedelta(minutes=2),
        )
    ]

    db_stub = DBStub(
        {
            User: [user],
            Lead: leads,
            Appointment: appts,
            FlowVersioned: [flow],
            Session: [session],
            Message: messages,
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

    yield TestClient(app), tenant_id, leads[0], appts[0], flow, session

    app.dependency_overrides.clear()


def test_panel_e2e_flow(test_client):
    client, tenant_id, lead, appt, flow, session = test_client

    # Login panel
    login_resp = client.post(
        "/v1/auth/login",
        json={"email": "user@example.com", "password": "secret"},
        headers={"X-Tenant-ID": tenant_id},
    )
    assert login_resp.status_code == 200
    access_token = login_resp.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {access_token}", "X-Tenant-ID": tenant_id}

    # Obtener leads
    leads_resp = client.get("/v1/leads", headers=auth_headers)
    assert leads_resp.status_code == 200
    leads_data = leads_resp.json()
    assert leads_data["total"] >= 1
    assert any(item["id"] == str(lead.id) for item in leads_data["items"])

    # Obtener citas
    appt_resp = client.get("/v1/appointments", headers=auth_headers)
    assert appt_resp.status_code == 200
    appt_items = appt_resp.json()["items"]
    assert any(item["id"] == str(appt.id) for item in appt_items)

    # Obtener flujo
    flow_resp = client.get("/v1/flows/current", headers=auth_headers)
    assert flow_resp.status_code == 200
    flow_data = flow_resp.json()
    assert flow_data["version"] == flow.version
    assert flow_data["tenant_id"] == tenant_id

    # Abrir lead
    lead_resp = client.get(f"/v1/leads/{lead.id}", headers=auth_headers)
    assert lead_resp.status_code == 200
    assert lead_resp.json()["id"] == str(lead.id)

    # Comprobar estado de sesión
    session_resp = client.get(f"/v1/sessions/{session.id}", headers=auth_headers)
    assert session_resp.status_code == 200
    session_data = session_resp.json()
    assert session_data["session_id"] == str(session.id)
    assert session_data["tenant_id"] == tenant_id
    assert session_data["state"] == session.state
