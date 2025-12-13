import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB


@compiles(JSONB, "sqlite")
def compile_jsonb(element, compiler, **kw):
    return "JSON"

from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models.tenants import Tenant
from app.models.sessions import Session as DBSess
from app.models.leads import Lead
from app.models.messages import Message
from app.main import get_application
from app.core.config import get_settings

# Skip when running with sqlite (jsonb defaults not supported)
pytestmark = pytest.mark.skipif(engine.dialect.name == "sqlite", reason="contract test requires postgres-like features")


@pytest.fixture(autouse=True, scope="module")
def _enable_sqlite():
    os.environ["DISABLE_DB"] = "1"
    os.environ["REDIS_URL"] = "memory://"
    os.environ["PANEL_API_TOKEN"] = "contracttoken"
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def setup_module():
    if os.getenv("DISABLE_DB") == "1":
        if engine.dialect.name == "sqlite":
            pytest.skip("SQLite does not support pg jsonb defaults used in this contract test", allow_module_level=True)
        Base.metadata.create_all(bind=engine)
        with SessionLocal() as db:
            if not db.query(Tenant).first():
                db.add(Tenant(id=uuid.uuid4(), name="Contract Tenant", contact_email="contract@example.com", plan="PRO"))
                db.commit()


def _client():
    return TestClient(get_application())


def test_chat_send_contract_flow_creates_session_lead_and_messages():
    client = _client()
    headers_base = {"x-api-key": "contracttoken"}
    session_uuid = uuid.uuid4()
    session_id_str = str(session_uuid)

    # limpiar restos
    with SessionLocal() as db:
        db.execute(delete(Message).where(Message.session_id == session_uuid))
        db.execute(delete(Lead).where(Lead.session_id == session_uuid))
        db.execute(delete(DBSess).where(DBSess.id == session_uuid))
        db.commit()

    seq = [
        "hola",  # welcome -> consent
        "consent_yes",
        "kitchen",
        "renovation",
        "3.2 x 2.4",
        "moderno",
        "5000",
        "este_ano",
        "Madrid",
        "continuar",  # avanzar mensaje de fotos opcional
        "Juan",
        "+34123456789",
        "",  # email opcional vacío
        "whatsapp",
        "home_measure",
        "score_warm_or_cold",
    ]

    last_resp = None
    for idx, msg in enumerate(seq):
        headers = {**headers_base, "Idempotency-Key": f"contract-{idx}"}
        payload = {"message": msg, "session_id": session_id_str}
        last_resp = client.post("/v1/chat/send", json=payload, headers=headers)
        assert last_resp.status_code == 200, last_resp.text

    data = last_resp.json()
    assert data["session_id"] == session_id_str

    with SessionLocal() as db:
        sess = db.query(DBSess).filter(DBSess.id == session_uuid).first()
        assert sess is not None
        tenant_id = sess.tenant_id
        lead = db.query(Lead).filter(Lead.session_id == session_uuid, Lead.tenant_id == tenant_id).first()
        assert lead is not None
        msgs = db.query(Message).filter(Message.session_id == session_uuid, Message.tenant_id == tenant_id).all()
        assert len(msgs) >= len(seq)
