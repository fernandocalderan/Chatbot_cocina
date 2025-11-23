import uuid

from sqlalchemy.exc import IntegrityError

from app.db.session import SessionLocal
from app.models.tenants import Tenant
from app.models.users import User
from app.models.flows import Flow
from app.models.configs import Config
from app.core.security import get_password_hash


def seed_demo() -> None:
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter_by(name="Demo Studio").first()
        if not tenant:
            tenant = Tenant(
                id=uuid.uuid4(),
                name="Demo Studio",
                contact_email="demo@example.com",
                plan="Pro",
                idioma_default="es",
                timezone="Europe/Madrid",
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
                role="admin",
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
                role="admin",
            )
            db.add(master)
        else:
            if not master.hashed_password or not master.hashed_password.startswith("$2"):
                master.hashed_password = master_hashed
                db.add(master)

        flow = db.query(Flow).filter_by(tenant_id=tenant.id, version=1).first()
        if not flow:
            flow = Flow(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                version=1,
                estado="published",
                schema_json={
                    "blocks": [
                        {"id": "bienvenida", "type": "message", "text": "Hola, ¿en qué podemos ayudarte?"},
                        {"id": "contacto", "type": "input", "field": "telefono"},
                    ]
                },
            )
            db.add(flow)

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

        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo()
