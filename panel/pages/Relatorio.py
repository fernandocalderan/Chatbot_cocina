import streamlit as st

from auth import ensure_login
from nav import legacy_redirect, nav_v2_enabled
from utils import load_styles

st.set_page_config(page_title="Relatorio", page_icon="🧾", layout="wide")
load_styles()
ensure_login()

# Debe depender de un lead_id; si no, cae a Oportunidades.
try:
    lead_id = st.query_params.get("lead_id")
    if isinstance(lead_id, list):
        lead_id = lead_id[0] if lead_id else None
    lead_id = str(lead_id) if lead_id else None
except Exception:
    lead_id = None

if lead_id:
    st.session_state["selected_lead_id"] = lead_id
    try:
        st.query_params["lead_id"] = lead_id
    except Exception:
        pass
    if nav_v2_enabled():
        legacy_redirect("/Relatorio", "pages/oportunidades.py")
    else:
        legacy_redirect("/Relatorio", "pages/08_Relatorio.py")
else:
    st.session_state.pop("selected_lead_id", None)
    legacy_redirect(
        "/Relatorio",
        "pages/oportunidades.py" if nav_v2_enabled() else "pages/02_Oportunidades.py",
        flash_message="Selecciona una oportunidad para continuar.",
    )
st.stop()
