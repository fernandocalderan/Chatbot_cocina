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
from app.models.sessions import Session


class QueryStub:
    def __init__(self, data: List[Any]):
        self.data = list(data)
        self._offset = 0
        self._limit = None

    def filter(self, *conditions):
        filtered = self.data
        for cond in conditions:
            left_key = getattr(getattr(cond, "left", None), "key", None)
            right = getattr(cond, "right", None)
            right_val = getattr(right, "value", right)
            if left_key is None:
                continue
            filtered = [row for row in filtered if getattr(row, left_key, None) == right_val]
        self.data = filtered
        return self

    def filter_by(self, **kwargs):
        filtered = self.data
        for key, value in kwargs.items():
            filtered = [row for row in filtered if getattr(row, key, None) == value]
        self.data = filtered
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


@pytest.fixture(autouse=True)
def setup_env():
    os.environ["DISABLE_DB"] = "1"
    settings = get_settings()
    settings.jwt_secret = None
    settings.panel_api_token = None
    yield
    os.environ.pop("DISABLE_DB", None)


@pytest.fixture
def client_with_data(monkeypatch):
    tenant_a = "tenant-a"
    tenant_b = "tenant-b"
    session_a = Session(
        id="sess-a",
        tenant_id=tenant_a,
        canal="web",
        idioma_detectado="es",
        state="welcome",
        last_block_id="welcome",
        variables_json={"foo": "bar"},
        expires_at=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    leads = [
        Lead(
            id="lead-a1",
            tenant_id=tenant_a,
            session_id=session_a.id,
            status="hot",
            score=80,
            score_breakdown_json={"budget": {"score": 80, "weight": 50}},
            meta_data={"contact_name": "Ana A", "contact_phone": "+34111111", "project_type": "kitchen"},
            created_at=datetime.now(timezone.utc) - timedelta(hours=3),
        ),
        Lead(
            id="lead-b1",
            tenant_id=tenant_b,
            session_id="sess-b",
            status="warm",
            score=40,
            score_breakdown_json={},
            meta_data={"contact_name": "B", "contact_phone": "+34222222"},
            created_at=datetime.now(timezone.utc) - timedelta(hours=2),
        ),
    ]
    appts = [
        Appointment(
            id="appt-a1",
            tenant_id=tenant_a,
            lead_id=leads[0].id,
            slot_start=datetime.now(timezone.utc) + timedelta(days=1),
            slot_end=datetime.now(timezone.utc) + timedelta(days=1, minutes=30),
            origen="demo",
            estado="booked",
            notas=None,
        ),
        Appointment(
            id="appt-b1",
            tenant_id=tenant_b,
            lead_id=leads[1].id,
            slot_start=datetime.now(timezone.utc) + timedelta(days=1),
            slot_end=datetime.now(timezone.utc) + timedelta(days=1, minutes=30),
            origen="demo",
            estado="booked",
            notas=None,
        ),
    ]
    flows = [
        FlowVersioned(
            id="flow-a",
            tenant_id=tenant_a,
            version=2,
            schema_json={"blocks": {"welcome": {"type": "message"}}, "version": 2},
            estado="published",
            published_at=datetime.now(timezone.utc),
        ),
        FlowVersioned(
            id="flow-b",
            tenant_id=tenant_b,
            version=1,
            schema_json={"blocks": {}, "version": 1},
            estado="published",
            published_at=datetime.now(timezone.utc),
        ),
    ]
    datasets = {Lead: leads, Appointment: appts, FlowVersioned: flows, Session: [session_a]}
    db_stub = DBStub(datasets)

    def override_get_db():
        try:
            yield db_stub
        finally:
            db_stub.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app), tenant_a, leads, appts, flows

    app.dependency_overrides.clear()


def test_contract_leads_schema_and_scoping(client_with_data):
    client, tenant_id, leads, _, _ = client_with_data
    resp = client.get("/v1/leads", headers={"X-Tenant-ID": tenant_id})
    assert resp.status_code == 200
    data = resp.json()
    assert set(data.keys()) >= {"items", "total", "page", "limit"}
    assert all(isinstance(item, dict) for item in data["items"])
    required = {"id", "session_id", "status", "score", "score_breakdown", "metadata", "created_at"}
    for item in data["items"]:
        assert set(item.keys()) >= required
    returned_ids = {item["id"] for item in data["items"]}
    assert "lead-a1" in returned_ids
    assert "lead-b1" not in returned_ids  # no datos de otros tenants


def test_contract_appointments_schema_and_scoping(client_with_data):
    client, tenant_id, _, appts, _ = client_with_data
    resp = client.get("/v1/appointments", headers={"X-Tenant-ID": tenant_id})
    assert resp.status_code == 200
    data = resp.json()
    assert set(data.keys()) >= {"items", "total", "page", "limit"}
    required = {"id", "lead_id", "slot_start", "slot_end", "visit_type", "status", "notas"}
    for item in data["items"]:
        assert set(item.keys()) >= required
    returned_ids = {item["id"] for item in data["items"]}
    assert "appt-a1" in returned_ids
    assert "appt-b1" not in returned_ids


def test_contract_flow_current_schema_and_scoping(client_with_data):
    client, tenant_id, _, _, flows = client_with_data
    resp = client.get("/v1/flows/current", headers={"X-Tenant-ID": tenant_id})
    assert resp.status_code == 200
    data = resp.json()
    required = {"tenant_id", "flow_id", "version", "estado", "published_at", "flow"}
    assert set(data.keys()) >= required
    assert data["tenant_id"] == tenant_id
    assert data["flow_id"] == flows[0].id
    assert data["version"] == flows[0].version
