import uuid
from datetime import datetime, timedelta, timezone

from app.db.session import SessionLocal
from app.models.leads import Lead
from app.models.appointments import Appointment

TENANT_ID = "3ef65ee3-b31a-4b48-874e-d8d937cb7766"


def run():
    db = SessionLocal()
    try:
        # Limpia leads previos con mismos emails para evitar duplicados
        emails = [
            "carlos.mendez@testmail.com",
            "laura.sanchez@testmail.com",
            "jose.ramirez@testmail.com",
            "marta.puig@testmail.com",
            "andres.lopez@testmail.com",
        ]
        db.query(Appointment).filter(Appointment.tenant_id == TENANT_ID).delete()
        db.query(Lead).filter(Lead.tenant_id == TENANT_ID, Lead.meta_data["contact_email"].astext.in_(emails)).delete(synchronize_session=False)
        db.commit()

        now = datetime.now(timezone.utc)
        leads_data = [
            {
                "id": uuid.uuid4(),
                "tenant_id": TENANT_ID,
                "source": "web",
                "origen": "web",
                "status": "cita_confirmada",
                "score": 92,
                "meta_data": {
                    "contact_name": "Carlos Méndez",
                    "contact_phone": "+34 611 234 001",
                    "contact_email": "carlos.mendez@testmail.com",
                    "budget_eur": 35000,
                    "urgency": "alta",
                    "area_m2": 18,
                    "style": "moderna",
                    "prioridad": "alta",
                },
            },
            {
                "id": uuid.uuid4(),
                "tenant_id": TENANT_ID,
                "source": "whatsapp",
                "origen": "whatsapp",
                "status": "en_seguimiento",
                "score": 68,
                "meta_data": {
                    "contact_name": "Laura Sánchez",
                    "contact_phone": "+34 611 234 002",
                    "contact_email": "laura.sanchez@testmail.com",
                    "budget_eur": 18000,
                    "urgency": "media",
                    "area_m2": 12,
                    "style": "nordica",
                    "prioridad": "media",
                },
            },
            {
                "id": uuid.uuid4(),
                "tenant_id": TENANT_ID,
                "source": "web",
                "origen": "web",
                "status": "nuevo",
                "score": 32,
                "meta_data": {
                    "contact_name": "José Ramírez",
                    "contact_phone": "+34 611 234 003",
                    "contact_email": "jose.ramirez@testmail.com",
                    "budget_eur": 9000,
                    "urgency": "baja",
                    "area_m2": 9,
                    "style": "indefinido",
                    "prioridad": "baja",
                },
            },
            {
                "id": uuid.uuid4(),
                "tenant_id": TENANT_ID,
                "source": "instagram_ads",
                "origen": "instagram_ads",
                "status": "nuevo",
                "score": 85,
                "meta_data": {
                    "contact_name": "Marta Puig",
                    "contact_phone": "+34 611 234 004",
                    "contact_email": "marta.puig@testmail.com",
                    "budget_eur": 27000,
                    "urgency": "alta",
                    "area_m2": 15,
                    "style": "industrial",
                    "prioridad": "alta",
                },
            },
            {
                "id": uuid.uuid4(),
                "tenant_id": TENANT_ID,
                "source": "referido",
                "origen": "referido",
                "status": "cita_programada",
                "score": 74,
                "meta_data": {
                    "contact_name": "Andrés López",
                    "contact_phone": "+34 611 234 005",
                    "contact_email": "andres.lopez@testmail.com",
                    "budget_eur": 22000,
                    "urgency": "media",
                    "area_m2": 14,
                    "style": "clasica",
                    "prioridad": "media",
                },
            },
        ]

        leads = [Lead(**ld) for ld in leads_data]
        db.add_all(leads)

        # Citas: lead 1 hoy, lead 5 en +3 días
        lead1_id = leads_data[0]["id"]
        lead5_id = leads_data[4]["id"]
        appt_today = Appointment(
            tenant_id=TENANT_ID,
            lead_id=lead1_id,
            slot_start=now + timedelta(hours=1),
            slot_end=now + timedelta(hours=2),
            estado="confirmed",
            origen="demo_seed",
            notas="Cita demo hoy",
        )
        appt_future = Appointment(
            tenant_id=TENANT_ID,
            lead_id=lead5_id,
            slot_start=now + timedelta(days=3),
            slot_end=now + timedelta(days=3, hours=1),
            estado="booked",
            origen="demo_seed",
            notas="Cita demo futura",
        )
        db.add_all([appt_today, appt_future])

        db.commit()
        print("✅ Seed de leads demo completado.")
    except Exception as exc:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
