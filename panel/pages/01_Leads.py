import pandas as pd
import streamlit as st

from api_client import list_leads
from auth import ensure_login
from utils import format_timestamp, load_styles

load_styles()
if "token" not in st.session_state:
    st.switch_page("auth.py")
ensure_login()

st.title("Leads")
leads = list_leads()

if not leads:
    st.info("No hay leads disponibles.")
else:
    rows = []
    for lead in leads:
        meta = lead.get("metadata") or {}
        rows.append(
            {
                "Nombre": meta.get("contact_name"),
                "Teléfono": meta.get("contact_phone"),
                "Proyecto": meta.get("project_type"),
                "Score": lead.get("score"),
                "Urgencia": meta.get("urgency"),
                "Fecha creación": format_timestamp(lead.get("created_at")),
                "session_id": lead.get("session_id"),
            }
        )

    df = pd.DataFrame(rows, columns=["Nombre", "Teléfono", "Proyecto", "Score", "Urgencia", "Fecha creación"])
    st.dataframe(df, use_container_width=True, hide_index=True)

    for i, lead in enumerate(leads):
        cols = st.columns(2)
        if cols[0].button("Ver historial", key=f"hist_{i}"):
            session_id = lead.get("session_id")
            st.session_state["session"] = session_id
            st.session_state["session_id"] = session_id
            st.switch_page("pages/03_Historial.py")
        if cols[1].button("Ver citas", key=f"citas_{i}"):
            st.session_state["lead_id"] = lead.get("id")
            st.switch_page("pages/02_Citas.py")
