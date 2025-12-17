import streamlit as st

from auth import ensure_login
from utils import load_styles
from api_client import list_appointments, confirm_appointment, cancel_appointment, get_lead
from crm_ui import format_time, format_day, day_bucket, human_status, lead_person  # noqa: E402
from datetime import datetime, timezone

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None

st.set_page_config(page_title="Agenda", page_icon="📅", layout="wide")
load_styles()
ensure_login()

st.title("Agenda")
st.caption("Hoy y próximos días, con acciones rápidas.")

appts = list_appointments() or []

tenant_tz = st.session_state.get("tenant_timezone", "Europe/Madrid")


@st.cache_data(ttl=60)
def _lead_display(lead_id: str) -> str:
    lead = get_lead(lead_id) or {}
    if isinstance(lead, dict) and lead.get("status_code"):
        return "Lead"
    return lead_person(lead).display_name


def _open_lead(lead_id: str):
    st.session_state["selected_lead_id"] = lead_id
    try:
        st.query_params["lead_id"] = str(lead_id)
    except Exception:
        pass
    try:
        st.switch_page("pages/08_Relatorio.py")
    except Exception:
        pass


if not appts:
    st.info("No tienes citas hoy. Buen momento para contactar oportunidades pendientes.\n\nEl asistente seguirá captando oportunidades.")
    st.stop()

# Ordenar y separar por fecha (sin timestamps crudos)
today = None
tz_obj = ZoneInfo(tenant_tz) if ZoneInfo else timezone.utc
today = datetime.now(tz=tz_obj).date()

today_items: list[dict] = []
upcoming_items: list[dict] = []
for a in appts:
    d = format_day(a.get("slot_start"), tz_name=tenant_tz)
    if not d:
        continue
    if d == today:
        today_items.append(a)
    elif d > today:
        upcoming_items.append(a)

st.subheader("HOY")
if not today_items:
    st.markdown("No tienes citas hoy. Buen momento para contactar oportunidades pendientes.")
else:
    for appt in sorted(today_items, key=lambda x: x.get("slot_start") or ""):
        lead_id = appt.get("lead_id")
        name = _lead_display(str(lead_id)) if lead_id else "Lead"
        hour = format_time(appt.get("slot_start"), tz_name=tenant_tz)
        visit_type = (appt.get("visit_type") or "").lower()
        tipo = "Llamada" if visit_type in {"chat", "call", "llamada"} else "Visita"
        st.markdown(f"**🕙 {hour} — {name}**")
        st.caption(f"{tipo} · {human_status(appt.get('status'))}")
        c = st.columns([0.25, 0.25, 0.25, 0.25])
        if lead_id and c[0].button("Ver lead", key=f"view-today-{appt.get('id')}", use_container_width=True):
            _open_lead(str(lead_id))
        if appt.get("id") and appt.get("status") != "confirmed" and c[1].button("Confirmar", key=f"confirm-{appt.get('id')}", use_container_width=True):
            confirm_appointment(str(appt.get("id")))
            st.success("Cita confirmada.")
            st.rerun()
        if appt.get("id") and c[2].button("Cancelar", key=f"cancel-{appt.get('id')}", use_container_width=True):
            cancel_appointment(str(appt.get("id")))
            st.success("Cita cancelada.")
            st.rerun()
        c[3].write("")

st.subheader("PRÓXIMOS DÍAS")
if not upcoming_items:
    st.caption("Sin citas próximas.")
else:
    buckets: dict[str, list[dict]] = {"Mañana": [], "Esta semana": [], "Próximos días": []}
    for appt in upcoming_items:
        d = format_day(appt.get("slot_start"), tz_name=tenant_tz)
        if not d:
            continue
        b = day_bucket(d, today)
        if b != "Hoy":
            buckets.setdefault(b, []).append(appt)

    for label in ("Mañana", "Esta semana", "Próximos días"):
        items = buckets.get(label) or []
        if not items:
            continue
        st.markdown(f"**{label}**")
        for appt in sorted(items, key=lambda x: x.get("slot_start") or ""):
            lead_id = appt.get("lead_id")
            name = _lead_display(str(lead_id)) if lead_id else "Lead"
            hour = format_time(appt.get("slot_start"), tz_name=tenant_tz)
            visit_type = (appt.get("visit_type") or "").lower()
            tipo = "Llamada" if visit_type in {"chat", "call", "llamada"} else "Visita"
            cols = st.columns([0.35, 0.25, 0.2, 0.2])
            cols[0].write(f"{hour} — {name}")
            cols[1].caption(tipo)
            cols[2].caption(human_status(appt.get("status")))
            if lead_id and cols[3].button("Ver lead", key=f"view-up-{appt.get('id')}", use_container_width=True):
                _open_lead(str(lead_id))
