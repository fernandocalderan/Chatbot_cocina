import streamlit as st

from auth import ensure_login
from nav import render_sidebar, legacy_redirect_with_tab, nav_v2_enabled
from utils import load_styles, empty_state

load_styles()
ensure_login()
if nav_v2_enabled():
    legacy_redirect_with_tab("/Flujo", "pages/automatizacion.py", "flujo")
    st.stop()
render_sidebar()

st.title("Flujo")
empty_state("Se movió a Automatización", "Ahora lo encuentras en Automatización → Cómo responde el asistente.", icon="🤖")
if st.button("Abrir Automatización", use_container_width=True):
    st.switch_page("pages/04_Automatizacion.py")
