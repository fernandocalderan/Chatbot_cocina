from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.auth import require_auth
from app.api.deps import get_db
from app.models.appointments import Appointment
from app.models.leads import Lead
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(prefix="/appointments", tags=["appointments"])


class BookingRequest(BaseModel):
    slot: str
    contact_name: str | None = None
    contact_phone: str | None = None
    session_id: str | None = None


@router.get("/slots", dependencies=[Depends(require_auth)])
def get_slots():
    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    slots = [
        (now + timedelta(hours=2)).isoformat() + "Z",
        (now + timedelta(hours=3)).isoformat() + "Z",
        (now + timedelta(hours=4)).isoformat() + "Z",
    ]
    return {"slots": slots}


@router.post("/book", dependencies=[Depends(require_auth)])
def book_slot(payload: BookingRequest, db=Depends(get_db)):
    slot_start = datetime.fromisoformat(payload.slot.replace("Z", "+00:00"))
    slot_end = slot_start + timedelta(minutes=30)

    lead_id = None
    tenant_id = None
    if payload.session_id:
        lead = db.query(Lead).filter(Lead.session_id == payload.session_id).first()
        if lead:
            lead_id = lead.id
            tenant_id = lead.tenant_id

    try:
        appt = Appointment(
            tenant_id=tenant_id,
            lead_id=lead_id,
            slot_start=slot_start,
            slot_end=slot_end,
            estado="booked",
            origen="chat",
            notas=None,
        )
        db.add(appt)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
    return {"status": "booked", "slot": payload.slot, "contact_name": payload.contact_name}
