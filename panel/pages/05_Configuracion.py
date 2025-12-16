import streamlit as st

from auth import ensure_login
from utils import load_styles

st.set_page_config(page_title="Configuración", page_icon="⚙️", layout="wide")
load_styles()
ensure_login()

st.title("Configuración")
st.caption("Plan, facturación, consumo y ajustes técnicos.")

st.subheader("Plan y facturación")
st.page_link("pages/06_Billing.py", label="Ir a Billing")

st.subheader("Consumo del asistente")
st.page_link("pages/04_📊_IA_Usage.py", label="Detalle técnico de IA")

st.subheader("Widget y dominios")
st.page_link("pages/07_Widget.py", label="Configurar widget y allowed origins")

st.subheader("Seguridad e idioma")
st.markdown("- Seguridad, idiomas y zona horaria (próximo)")
