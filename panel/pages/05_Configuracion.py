import streamlit as st

from auth import ensure_login
from nav import legacy_redirect
from utils import load_styles

st.set_page_config(page_title="Configuración", page_icon="⚙️", layout="wide")
load_styles()
ensure_login()
# Legacy route: redirige siempre a la Configuración V2.
st.session_state["_config_tab"] = st.session_state.get("_config_tab") or "billing"
legacy_redirect("/Configuracion", "pages/configuracion.py")
st.stop()
