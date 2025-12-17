from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from html import escape
from typing import Any

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore


STATUS_MAP = {
    "NUEVO": "Nuevo",
    "EN_SEGUIMIENTO": "En seguimiento",
    "CITA_PROGRAMADA": "Cita programada",
    "CITA_CONFIRMADA": "Cita confirmada",
    "PERDIDO": "Perdido",
}


def _norm(s: str | None) -> str:
    return str(s or "").strip()


def human_status(status: str | None) -> str:
    raw = _norm(status)
    if not raw:
        return "Nuevo"
    if raw in STATUS_MAP:
        return STATUS_MAP[raw]
    val = raw.strip().lower()
    mapping = {
        "nuevo": "Nuevo",
        "new": "Nuevo",
        "hot": "En seguimiento",
        "warm": "En seguimiento",
        "cold": "En seguimiento",
        "en_seguimiento": "En seguimiento",
        "contactado": "En seguimiento",
        "en_propuesta": "En seguimiento",
        "negociación": "En seguimiento",
        "negociacion": "En seguimiento",
        "booked": "Cita programada",
        "cita_programada": "Cita programada",
        "cita": "Cita programada",
        "confirmed": "Cita confirmada",
        "cita_confirmada": "Cita confirmada",
        "canceled": "Cancelada",
        "cancelled": "Cancelada",
        "cancelada": "Cancelada",
        "lost": "Perdido",
        "perdido": "Perdido",
    }
    if val in mapping:
        return mapping[val]
    return raw[:1].upper() + raw[1:]


def priority_label(lead: dict[str, Any]) -> str:
    prio = lead.get("priority")
    if isinstance(prio, str):
        val = prio.lower()
        if "high" in val or "alta" in val or "🔥" in val:
            return "🔥 Alta"
        if "med" in val or "media" in val or "⚡" in val:
            return "⚡ Media"
        if "low" in val or "baja" in val or "❄️" in val:
            return "❄️ Baja"
    score = lead.get("score")
    try:
        score_val = float(score) if score is not None else None
    except Exception:
        score_val = None
    if score_val is None:
        return "⚡ Media"
    if score_val >= 70:
        return "🔥 Alta"
    if score_val >= 40:
        return "⚡ Media"
    return "❄️ Baja"


def parse_iso_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def _tz(tz_name: str | None) -> timezone | Any:
    if not tz_name or not ZoneInfo:
        return timezone.utc
    try:
        return ZoneInfo(tz_name)
    except Exception:
        return timezone.utc


def relative_time(value: str | None, tz_name: str | None = None, now: datetime | None = None) -> str:
    dt = parse_iso_dt(value)
    if not dt:
        return ""
    tz = _tz(tz_name)
    now_dt = now or datetime.now(tz=tz)
    dt_local = dt.astimezone(tz)
    delta = now_dt - dt_local
    seconds = int(delta.total_seconds())
    if seconds < 0:
        seconds = 0
    if seconds < 60:
        return "Hace 1m"
    if seconds < 3600:
        mins = max(1, seconds // 60)
        return f"Hace {mins}m"
    if seconds < 86400:
        hours = max(1, seconds // 3600)
        return f"Hace {hours}h"
    days = max(1, seconds // 86400)
    if days == 1:
        return "Ayer"
    return f"Hace {days} días"


def format_time(value: str | None, tz_name: str | None = None) -> str:
    dt = parse_iso_dt(value)
    if not dt:
        return ""
    tz = _tz(tz_name)
    return dt.astimezone(tz).strftime("%H:%M")


def format_day(value: str | None, tz_name: str | None = None) -> date | None:
    dt = parse_iso_dt(value)
    if not dt:
        return None
    tz = _tz(tz_name)
    return dt.astimezone(tz).date()


def day_bucket(d: date, today: date) -> str:
    if d == today:
        return "Hoy"
    if d == today + timedelta(days=1):
        return "Mañana"
    if d <= today + timedelta(days=7):
        return "Esta semana"
    return "Próximos días"


def human_project_type(value: str | None) -> str:
    v = _norm(value).lower()
    if not v:
        return ""
    mapping = {
        "kitchen": "Cocina",
        "cocina": "Cocina",
        "armario": "Armario",
        "wardrobe": "Armario",
        "mueble": "Mueble",
        "furniture": "Mueble",
    }
    return mapping.get(v, value or "")


def human_urgency(value: str | None) -> str:
    v = _norm(value).lower()
    if not v:
        return ""
    mapping = {
        "sin_prisa": "Sin prisa",
        "este_ano": "Este año",
        "este_trimestre": "Este trimestre",
        "urgente_30_dias": "Urgente (30 días)",
        "urgente": "Urgente",
    }
    return mapping.get(v, value or "")


def safe_chat_html(text: str) -> str:
    return escape(text or "").replace("\n", "<br/>")


@dataclass(frozen=True)
class LeadPerson:
    display_name: str
    phone: str | None = None
    email: str | None = None
    company: str | None = None


def lead_person(lead: dict[str, Any]) -> LeadPerson:
    meta = lead.get("metadata") if isinstance(lead.get("metadata"), dict) else {}
    name = (
        meta.get("contact_name")
        or meta.get("name")
        or lead.get("name")
        or ""
    )
    phone = meta.get("contact_phone") or meta.get("phone") or None
    email = meta.get("contact_email") or meta.get("email") or None
    company = meta.get("company") or meta.get("business_name") or meta.get("cliente") or meta.get("client") or None
    display_name = str(name or email or phone or "Recién llegado").strip()
    return LeadPerson(display_name=display_name, phone=phone, email=email, company=company)


def recommended_action(lead_status: str | None, has_appointment: bool = False) -> str:
    hs = human_status(lead_status)
    if hs == "Perdido":
        return ""
    if hs == "Cita confirmada":
        return "Ver / crear cita"
    if hs == "Cita programada" or has_appointment:
        return "Confirmar cita"
    return "Llamar hoy"


def quote_status_human(value: str | None) -> str:
    v = _norm(value).lower()
    if v in {"generated", "generado"}:
        return "Generado"
    if v in {"sent", "enviado"}:
        return "Enviado"
    return "Pendiente"
