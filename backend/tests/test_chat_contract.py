import os
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models.tenants import Tenant
from app.models.sessions import Session as DBSess
from app.models.leads import Lead
from app.models.messages import Message
from app.main import get_application
from app.core.config import get_settings


def setup_module():
    # Real DB, redis en memoria para velocidad
    os.environ.pop("DISABLE_DB", None)
    os.environ["REDIS_URL"] = "memory://"
    os.environ["PANEL_API_TOKEN"] = "contracttoken"
    get_settings.cache_clear()

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if not db.query(Tenant).first():
            db.add(Tenant(id=uuid.uuid4(), name="Contract Tenant", contact_email="contract@example.com", plan="Pro"))
            db.commit()


def _client():
    return TestClient(get_application())


def test_chat_send_contract_flow_creates_session_lead_and_messages():
    client = _client()
    headers_base = {"x-api-key": "contracttoken"}
    session_id = str(uuid.uuid4())

    # limpiar restos
    with SessionLocal() as db:
        db.execute(delete(Message).where(Message.session_id == session_id))
        db.execute(delete(Lead).where(Lead.session_id == session_id))
        db.execute(delete(DBSess).where(DBSess.id == session_id))
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
        payload = {"message": msg, "session_id": session_id}
        last_resp = client.post("/v1/chat/send", json=payload, headers=headers)
        assert last_resp.status_code == 200, last_resp.text

    data = last_resp.json()
    assert data["session_id"] == session_id

    with SessionLocal() as db:
        sess = db.query(DBSess).filter(DBSess.id == session_id).first()
        assert sess is not None
        tenant_id = sess.tenant_id
        lead = db.query(Lead).filter(Lead.session_id == session_id, Lead.tenant_id == tenant_id).first()
        assert lead is not None
        msgs = db.query(Message).filter(Message.session_id == session_id, Message.tenant_id == tenant_id).all()
        assert len(msgs) >= len(seq)
