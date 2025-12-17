import streamlit as st

from auth import ensure_login
from utils import load_styles, empty_state, loading_state, pill
from nav import render_sidebar, legacy_redirect, nav_v2_enabled
from api_client import list_leads

st.set_page_config(page_title="Oportunidades", page_icon="📈", layout="wide")
load_styles()
ensure_login()
if nav_v2_enabled():
    legacy_redirect("/Oportunidades", "pages/oportunidades.py")
    st.stop()
render_sidebar()

from crm_ui import (  # noqa: E402
    human_status,
    priority_label,
    relative_time,
    lead_person,
    recommended_action,
)

def _open_lead(lead_id: str):
    st.session_state["selected_lead_id"] = lead_id
    try:
        st.query_params["lead_id"] = lead_id
    except Exception:
        pass
    try:
        st.switch_page("pages/08_Relatorio.py")
    except Exception:
        st.rerun()


st.title("Oportunidades")
st.caption("Prioriza acciones comerciales: personas primero, datos solo si ayudan.")

loader = st.empty()
with loader.container():
    loading_state()
leads = list_leads() or []
loader.empty()

filters = st.columns(4)
show_new = filters[0].checkbox("Nuevos", value=False)
show_high = filters[1].checkbox("Prioridad alta", value=False)
show_with_appt = filters[2].checkbox("Con cita", value=False)
show_no_contact = filters[3].checkbox("Sin contactar", value=False)

tenant_tz = st.session_state.get("tenant_timezone", "Europe/Madrid")

def _last_contact_text(lead: dict) -> str:
    last = lead.get("last_activity_at") or lead.get("updated_at") or lead.get("created_at")
    txt = relative_time(last, tz_name=tenant_tz)
    if not txt:
        return ""
    if human_status(lead.get("status")) == "Nuevo" and not lead.get("last_activity_at"):
        return "Recién llegado"
    return txt


filtered = []
for lead in leads:
    status = human_status(lead.get("status"))
    prio = priority_label(lead)
    has_appt = status in {"Cita programada", "Cita confirmada"}
    if show_new and status != "Nuevo":
        continue
    if show_high and prio != "🔥 Alta":
        continue
    if show_with_appt and not has_appt:
        continue
    if show_no_contact and lead.get("last_activity_at"):
        continue
    filtered.append(lead)

if not filtered:
    empty_state("Sin oportunidades nuevas", "Buen momento para revisar los leads en seguimiento o preparar las citas.", icon="📈")
    st.stop()

# Tabla (sin IDs ni timestamps crudos)
header = st.columns([1.7, 1.3, 1.2, 1.2, 0.9, 1.1, 1.4, 0.9])
header[0].markdown("**Cliente**")
header[1].markdown("**Nombre**")
header[2].markdown("**Teléfono**")
header[3].markdown("**Estado**")
header[4].markdown("**Prioridad**")
header[5].markdown("**Último contacto**")
header[6].markdown("**Acción recomendada**")
header[7].markdown("**Acciones**")

for lead in filtered:
    pid = lead.get("id")
    if not pid:
        continue
    p = lead_person(lead)
    status = human_status(lead.get("status"))
    prio = priority_label(lead)
    last_txt = _last_contact_text(lead)
    action = recommended_action(lead.get("status"), has_appointment=status in {"Cita programada", "Cita confirmada"})

    row = st.columns([1.7, 1.3, 1.2, 1.2, 0.9, 1.1, 1.4, 0.9])
    row[0].write(p.company or p.display_name)
    row[1].write(p.display_name if p.company else "")
    if p.phone:
        row[2].markdown(f"[📞 {p.phone}](tel:{p.phone})")
    else:
        row[2].write("")
    row[3].markdown(pill(status, tone="info"), unsafe_allow_html=True)
    pr_tone = "danger" if prio.startswith("🔥") else ("warning" if prio.startswith("⚡") else "info")
    row[4].markdown(pill(prio, tone=pr_tone), unsafe_allow_html=True)
    row[5].write(last_txt)
    row[6].write(action)
    if row[7].button("Ver detalles", key=f"view-{pid}", use_container_width=True):
        _open_lead(str(pid))
