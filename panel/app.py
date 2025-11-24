import streamlit as st

from auth import ensure_login
from utils import load_styles

st.set_page_config(page_title="Panel Operativo", layout="wide")
load_styles()

# Redirige al login si no hay token
if "token" not in st.session_state:
    try:
        st.switch_page("pages/auth.py")
    except Exception:
        st.stop()
ensure_login()

st.title("Panel operativo")
st.write("Usa el menú lateral para navegar por Leads, Citas, Historial, Scoring y Flujo.")

st.info(
    "Tip: el login usa /v1/auth/login del backend. Configura API_BASE, PANEL_EMAIL y "
    "PANEL_PASSWORD en tus variables de entorno para autocompletar."
)
