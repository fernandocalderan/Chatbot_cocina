from datetime import datetime, timedelta

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/appointments", tags=["appointments"])


class BookingRequest(BaseModel):
    slot: str
    contact_name: str | None = None
    contact_phone: str | None = None


@router.get("/slots")
def get_slots():
    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    slots = [
        (now + timedelta(hours=2)).isoformat() + "Z",
        (now + timedelta(hours=3)).isoformat() + "Z",
        (now + timedelta(hours=4)).isoformat() + "Z",
    ]
    return {"slots": slots}


@router.post("/book")
def book_slot(payload: BookingRequest):
    # Stub: devuelve el slot confirmado
    return {"status": "booked", "slot": payload.slot, "contact_name": payload.contact_name}
