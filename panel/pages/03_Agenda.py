import streamlit as st

from auth import ensure_login
from utils import load_styles
from api_client import list_appointments, confirm_appointment, cancel_appointment

st.set_page_config(page_title="Agenda", page_icon="📅", layout="wide")
load_styles()
ensure_login()

st.title("Agenda")
st.caption("Hoy y próximos días, con acciones rápidas.")

appts = list_appointments() or []

if not appts:
    st.info("Aún no hay citas programadas. El asistente seguirá captando oportunidades automáticamente.")
else:
    today = []
    upcoming = []
    from datetime import datetime, date

    for a in appts:
        is_today = bool(a.get("is_today"))
        if not is_today and a.get("slot_start"):
            try:
                slot_dt = datetime.fromisoformat(a.get("slot_start").replace("Z", "+00:00"))
                is_today = slot_dt.date() == date.today()
            except Exception:
                is_today = False
        if is_today:
            today.append(a)
        else:
            upcoming.append(a)

    def render_list(title, items):
        st.subheader(title)
        if not items:
            st.caption("Sin citas en esta sección.")
            return
        for appt in items:
            header = f"{appt.get('slot_start') or '—'} — {appt.get('contact_name') or 'Lead'}"
            with st.expander(header):
                st.markdown(f"**Estado:** {appt.get('estado') or '—'}")
                st.markdown(f"**Notas:** {appt.get('notas') or '—'}")
                cols = st.columns(2)
                if appt.get("id") and cols[0].button("Confirmar", key=f"c-{appt.get('id')}"):
                    confirm_appointment(appt.get("id"))
                    st.success("Cita confirmada.")
                if appt.get("id") and cols[1].button("Cancelar", key=f"x-{appt.get('id')}"):
                    cancel_appointment(appt.get("id"))
                    st.warning("Cita cancelada.")

    render_list("Hoy", today)
    render_list("Próximos días", upcoming)
