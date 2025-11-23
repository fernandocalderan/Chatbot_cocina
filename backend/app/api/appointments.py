from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.auth import oauth2_scheme, require_auth
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


class AppointmentAction(BaseModel):
    id: str


@router.get("/slots", dependencies=[Depends(require_auth)])
def get_slots(token: str = Depends(oauth2_scheme)):
    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    slots = [
        (now + timedelta(hours=2)).isoformat() + "Z",
        (now + timedelta(hours=3)).isoformat() + "Z",
        (now + timedelta(hours=4)).isoformat() + "Z",
    ]
    return {"slots": slots}


@router.post("/book", dependencies=[Depends(require_auth)])
def book_slot(payload: BookingRequest, db=Depends(get_db), token: str = Depends(oauth2_scheme)):
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


@router.get("/", dependencies=[Depends(require_auth)])
def list_appointments(db=Depends(get_db), token: str = Depends(oauth2_scheme)):
    appts = db.query(Appointment).order_by(Appointment.slot_start.desc()).all()
    return [
        {
            "id": str(appt.id),
            "lead_id": str(appt.lead_id) if appt.lead_id else None,
            "slot_start": appt.slot_start.isoformat() if appt.slot_start else None,
            "slot_end": appt.slot_end.isoformat() if appt.slot_end else None,
            "visit_type": appt.origen,
            "status": appt.estado,
        }
        for appt in appts
    ]


@router.post("/confirm", dependencies=[Depends(require_auth)])
def confirm_appointment(payload: AppointmentAction, db=Depends(get_db), token: str = Depends(oauth2_scheme)):
    appt = db.query(Appointment).filter(Appointment.id == payload.id).first()
    if not appt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="appointment_not_found")
    try:
        appt.estado = "confirmed"
        db.add(appt)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="error_updating_appointment")
    return {"id": str(appt.id), "status": appt.estado}


@router.post("/cancel", dependencies=[Depends(require_auth)])
def cancel_appointment(payload: AppointmentAction, db=Depends(get_db), token: str = Depends(oauth2_scheme)):
    appt = db.query(Appointment).filter(Appointment.id == payload.id).first()
    if not appt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="appointment_not_found")
    try:
        appt.estado = "cancelled"
        db.add(appt)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="error_updating_appointment")
    return {"id": str(appt.id), "status": appt.estado}
