import uuid

from sqlalchemy.exc import IntegrityError

from app.db.session import SessionLocal
from app.models.tenants import Tenant
from app.models.users import User
from app.models.flows import Flow
from app.models.configs import Config
from app.models.leads import Lead
from app.models.sessions import Session as DBSess
from app.models.appointments import Appointment
from app.core.security import get_password_hash
from app.services.template_service import TemplateService


def seed_demo() -> None:
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter_by(name="Demo Studio").first()
        if not tenant:
            tenant = Tenant(
                id=uuid.uuid4(),
                name="Demo Studio",
                contact_email="demo@example.com",
                plan="PRO",
                idioma_default="es",
                timezone="Europe/Madrid",
                flags_ia={"intent_extraction_enabled": True, "text_gen_enabled": True},
            )
            db.add(tenant)
            db.flush()

        user = db.query(User).filter_by(tenant_id=tenant.id, email="admin@demo.com").first()
        demo_hashed = get_password_hash("demo")
        if not user:
            user = User(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                email="admin@demo.com",
                hashed_password=demo_hashed,
                role="ADMIN",
            )
            db.add(user)
        else:
            if not user.hashed_password or user.hashed_password == "demo" or not user.hashed_password.startswith("$2"):
                user.hashed_password = demo_hashed
                db.add(user)

        master = db.query(User).filter_by(tenant_id=tenant.id, email="master@demo.com").first()
        master_hashed = get_password_hash("master123")
        if not master:
            master = User(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                email="master@demo.com",
                hashed_password=master_hashed,
                role="ADMIN",
            )
            db.add(master)
        else:
            if not master.hashed_password or not master.hashed_password.startswith("$2"):
                master.hashed_password = master_hashed
                db.add(master)

        flows = db.query(Flow).filter_by(tenant_id=tenant.id).all()
        if not flows:
            flow_simple = Flow(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                version=1,
                estado="published",
                schema_json={
                    "blocks": [
                        {"id": "welcome", "type": "message", "text": "Hola, ¿en qué podemos ayudarte?"},
                        {
                            "id": "ask_need",
                            "type": "options",
                            "text": "¿Buscas cocina o armario?",
                            "options": [
                                {"id": "cocina", "label_es": "Cocina"},
                                {"id": "armario", "label_es": "Armario"},
                            ],
                            "branches": {"cocina": "ask_budget", "armario": "ask_budget"},
                        },
                        {"id": "ask_budget", "type": "input", "text": "¿Presupuesto aproximado?", "next": "end"},
                        {"id": "end", "type": "message", "text": "Gracias, te contactamos pronto."},
                    ]
                },
            )
            flow_branch = Flow(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                version=2,
                estado="published",
                schema_json={
                    "blocks": [
                        {"id": "welcome", "type": "message", "text": "Hola, te ayudamos con tu proyecto."},
                        {
                            "id": "ask_visit",
                            "type": "options",
                            "text": "¿Quieres cita ya?",
                            "options": [
                                {"id": "si", "label_es": "Sí"},
                                {"id": "no", "label_es": "Prefiero info"},
                            ],
                            "branches": {"si": "ask_slot", "no": "summary"},
                        },
                        {
                            "id": "ask_slot",
                            "type": "appointment",
                            "text": "Elige día y hora",
                            "next": "summary",
                        },
                        {"id": "summary", "type": "message", "text": "Resumen enviado."},
                    ]
                },
            )
            db.add_all([flow_simple, flow_branch])

        config = db.query(Config).filter_by(tenant_id=tenant.id, tipo="response_times").first()
        if not config:
            config = Config(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                tipo="response_times",
                payload_json={"sla_seconds": 30},
                version=1,
            )
            db.add(config)

        agenda_cfg = db.query(Config).filter_by(tenant_id=tenant.id, tipo="agenda_rules").first()
        if not agenda_cfg:
            agenda_cfg = Config(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                tipo="agenda_rules",
                payload_json={
                    "days_ahead": 5,
                    "slot_minutes": 30,
                    "workdays": [0, 1, 2, 3, 4, 5],
                    "daily_ranges": [{"start": "10:00", "end": "14:00"}, {"start": "16:00", "end": "19:00"}],
                    "holidays": [],
                },
                version=1,
            )
            db.add(agenda_cfg)

        # Leads y citas de demo
        existing_lead = db.query(Lead).filter_by(tenant_id=tenant.id).first()
        if not existing_lead:
            sess_id = uuid.uuid4()
            session = DBSess(
                id=sess_id,
                tenant_id=tenant.id,
                canal="web",
                state="summary",
                variables_json={"project_type": "kitchen", "budget": "8000", "urgency": "este_ano"},
            )
            lead = Lead(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                session_id=sess_id,
                origen="demo",
                status="hot",
                score=85,
                score_breakdown_json={"budget": {"score": 70, "weight": 40}},
                meta_data={"contact_name": "Ana Demo", "contact_phone": "+34999000111"},
            )
            appt = Appointment(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                lead_id=lead.id,
                slot_start=None,
                slot_end=None,
                estado="booked",
                origen="demo",
                notas="Cita de demo",
            )
            db.add_all([session, lead, appt])

        db.commit()

        try:
            tpl = TemplateService.clone_default_template(db, str(tenant.id))
            if tpl:
                tenant.default_template_id = tpl.id
                db.add(tenant)
                db.commit()
        except Exception:
            db.rollback()
    except IntegrityError:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo()
