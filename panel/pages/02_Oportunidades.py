import streamlit as st

from auth import ensure_login
from utils import load_styles
from api_client import list_leads

st.set_page_config(page_title="Oportunidades", page_icon="📈", layout="wide")
load_styles()
ensure_login()

st.title("Oportunidades")
st.caption("Prioridad visual y acción recomendada.")

leads = list_leads() or []

filters = st.columns(4)
show_new = filters[0].checkbox("Nuevos", value=False)
show_high = filters[1].checkbox("Prioridad alta", value=False)
show_with_appt = filters[2].checkbox("Con cita", value=False)
show_no_contact = filters[3].checkbox("Sin contactar", value=False)

def priority_label(lead):
    score = lead.get("score")
    prio = lead.get("priority")
    if isinstance(prio, str):
        val = prio.lower()
        if "high" in val or "alta" in val or "🔥" in val:
            return "🔥 Alta"
        if "med" in val or "⚡" in val:
            return "⚡ Media"
        return "❄️ Baja"
    if score is None:
        return "⚡ Media"
    score = float(score)
    if score >= 70:
        return "🔥 Alta"
    if score >= 40:
        return "⚡ Media"
    return "❄️ Baja"

def status_label(lead):
    status = str(lead.get("status") or "").lower()
    mapping = {
        "new": "Nuevo",
        "hot": "En seguimiento",
        "warm": "En seguimiento",
        "booked": "Cita",
        "confirmed": "Cita",
        "lost": "Perdido",
    }
    return mapping.get(status, status.title() if status else "—")

def action_hint(lead):
    if lead.get("status") in ("booked", "confirmed"):
        return "Confirma o actualiza la cita"
    if lead.get("status") in ("new", None):
        return "Contacta hoy"
    return "Dar seguimiento"

def last_interaction(lead):
    return lead.get("updated_at") or lead.get("created_at") or "—"

rows = []
for lead in leads:
    prio = priority_label(lead)
    status = status_label(lead)
    if show_new and status != "Nuevo":
        continue
    if show_high and prio != "🔥 Alta":
        continue
    if show_with_appt and status != "Cita":
        continue
    if show_no_contact and lead.get("last_contact_at"):
        continue
    rows.append(
        {
            "Nombre / contacto": (lead.get("name") or lead.get("contact_name") or lead.get("email") or "—"),
            "Estado": status,
            "Prioridad": prio,
            "Última interacción": last_interaction(lead),
            "Acción recomendada": action_hint(lead),
        }
    )

if not rows:
    st.info("Aún no hay oportunidades nuevas.")
else:
    st.dataframe(rows, use_container_width=True, hide_index=True)
