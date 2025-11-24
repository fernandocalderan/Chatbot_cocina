from datetime import datetime, timedelta, date, timezone

from fastapi import APIRouter, Depends, HTTPException, Header, Query, status
from pydantic import BaseModel

from app.api.auth import oauth2_scheme, require_auth
from app.api.deps import get_db, get_tenant_id
from app.core.config import get_settings
from app.core.idempotency import IdempotencyStore
from app.models.appointments import Appointment
from app.models.leads import Lead
from app.models.configs import Config
from app.models.tenants import Tenant
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_

router = APIRouter(prefix="/appointments", tags=["appointments"])


class BookingRequest(BaseModel):
    slot: str
    contact_name: str | None = None
    contact_phone: str | None = None
    session_id: str | None = None


class AppointmentAction(BaseModel):
    id: str


class AppointmentUpdate(BaseModel):
    slot_start: str | None = None
    slot_end: str | None = None
    status: str | None = None
    notas: str | None = None


@router.get("/slots", dependencies=[Depends(require_auth)])
def get_slots(
    token: str = Depends(oauth2_scheme),
    tenant_id: str = Depends(get_tenant_id),
    visit_type: str | None = Query(default=None),
    db=Depends(get_db),
):
    cfg = (
        db.query(Config)
        .filter(Config.tenant_id == tenant_id, Config.tipo == "agenda_rules")
        .order_by(Config.version.desc())
        .first()
    )
    rules = cfg.payload_json if cfg else None
    from app.services.agenda_service import AgendaService

    svc = AgendaService(rules)
    slots = svc.get_slots(tenant_id=tenant_id, visit_type=visit_type, location=None, rules_override=rules)
    return {"slots": slots}


@router.post("/book", dependencies=[Depends(require_auth)])
def book_slot(
    payload: BookingRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    tenant_id: str = Depends(get_tenant_id),
    db=Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    settings = get_settings()
    if not idempotency_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="missing_idempotency_key")

    idemp_store = IdempotencyStore(settings.redis_url, namespace="idemp:appointments")
    payload_dict = payload.model_dump()
    cached = idemp_store.get(idempotency_key)
    if cached is not None:
        cached_payload = cached.get("payload")
        if cached_payload != payload_dict:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="idempotency_conflict")
        return cached.get("response")

    # Timezone tenant
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    tz_name = tenant.timezone if tenant else "UTC"
    try:
        import zoneinfo

        tzinfo = zoneinfo.ZoneInfo(tz_name)
    except Exception:
        tzinfo = timezone.utc

    try:
        slot_start_utc = datetime.fromisoformat(payload.slot.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid_slot")

    slot_minutes = 30
    cfg = (
        db.query(Config)
        .filter(Config.tenant_id == tenant_id, Config.tipo == "agenda_rules")
        .order_by(Config.version.desc())
        .first()
    )
    if cfg:
        slot_minutes = int(cfg.payload_json.get("slot_minutes", 30))
    slot_end_utc = slot_start_utc + timedelta(minutes=slot_minutes)

    # Evitar solapes
    overlap = (
        db.query(Appointment)
        .filter(
            Appointment.tenant_id == tenant_id,
            Appointment.slot_start < slot_end_utc,
            Appointment.slot_end > slot_start_utc,
        )
        .first()
    )
    if overlap:
        raise HTTPException(status_code=409, detail="slot_unavailable")

    lead_id = None
    if payload.session_id:
        lead = db.query(Lead).filter(Lead.session_id == payload.session_id, Lead.tenant_id == tenant_id).first()
        if lead:
            lead_id = lead.id

    try:
        appt = Appointment(
            tenant_id=tenant_id,
            lead_id=lead_id,
            slot_start=slot_start_utc,
            slot_end=slot_end_utc,
            estado="booked",
            origen="chat",
            notas=None,
        )
        db.add(appt)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="error_booking")
    response_data = {
        "status": "booked",
        "slot": payload.slot,
        "slot_utc": slot_start_utc.isoformat() + "Z",
        "slot_end_utc": slot_end_utc.isoformat() + "Z",
        "contact_name": payload.contact_name,
        "appointment_id": str(appt.id),
    }
    idemp_store.set(idempotency_key, {"payload": payload_dict, "response": response_data})
    return response_data


@router.get("/", dependencies=[Depends(require_auth)])
def list_appointments(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=200),
    fecha: date | None = Query(default=None),
    estado: str | None = Query(default=None),
    lead_id: str | None = Query(default=None),
    agente: str | None = Query(default=None),  # placeholder; sin campo dedicado
):
    q = db.query(Appointment).filter(Appointment.tenant_id == tenant_id)

    filters = []
    if fecha:
        start_dt = datetime.combine(fecha, datetime.min.time(), tzinfo=timezone.utc)
        end_dt = datetime.combine(fecha, datetime.max.time(), tzinfo=timezone.utc)
        filters.append(and_(Appointment.slot_start >= start_dt, Appointment.slot_start <= end_dt))
    if estado:
        filters.append(Appointment.estado == estado)
    if lead_id:
        filters.append(Appointment.lead_id == lead_id)
    # agente no existe en el modelo; se deja como placeholder sin efecto real
    if filters:
        q = q.filter(*filters)

    total = q.count()
    offset = (page - 1) * limit
    appts = q.order_by(Appointment.slot_start.desc()).offset(offset).limit(limit).all()
    items = [
        {
            "id": str(appt.id),
            "lead_id": str(appt.lead_id) if appt.lead_id else None,
            "slot_start": appt.slot_start.isoformat() if appt.slot_start else None,
            "slot_end": appt.slot_end.isoformat() if appt.slot_end else None,
            "visit_type": appt.origen,
            "status": appt.estado,
            "notas": appt.notas,
        }
        for appt in appts
    ]
    return {"items": items, "total": total, "page": page, "limit": limit}


@router.post("/confirm", dependencies=[Depends(require_auth)])
def confirm_appointment(
    payload: AppointmentAction,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    appt = db.query(Appointment).filter(Appointment.id == payload.id, Appointment.tenant_id == tenant_id).first()
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


@router.patch("/{appt_id}", dependencies=[Depends(require_auth)])
def update_appointment(
    appt_id: str,
    payload: AppointmentUpdate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    appt = db.query(Appointment).filter(Appointment.id == appt_id, Appointment.tenant_id == tenant_id).first()
    if not appt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="appointment_not_found")
    try:
        if payload.slot_start:
            appt.slot_start = datetime.fromisoformat(payload.slot_start.replace("Z", "+00:00"))
        if payload.slot_end:
            appt.slot_end = datetime.fromisoformat(payload.slot_end.replace("Z", "+00:00"))
        if payload.status:
            appt.estado = payload.status
        if payload.notas is not None:
            appt.notas = payload.notas
        db.add(appt)
        db.commit()
        db.refresh(appt)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="error_updating_appointment")
    return {
        "id": str(appt.id),
        "status": appt.estado,
        "slot_start": appt.slot_start.isoformat() if appt.slot_start else None,
        "slot_end": appt.slot_end.isoformat() if appt.slot_end else None,
        "notas": appt.notas,
    }


@router.post("/cancel", dependencies=[Depends(require_auth)])
def cancel_appointment(
    payload: AppointmentAction,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    appt = db.query(Appointment).filter(Appointment.id == payload.id, Appointment.tenant_id == tenant_id).first()
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
