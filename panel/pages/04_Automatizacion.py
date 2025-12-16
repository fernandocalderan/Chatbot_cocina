import streamlit as st

from auth import ensure_login
from utils import load_styles

st.set_page_config(page_title="Automatización", page_icon="🤖", layout="wide")
load_styles()
ensure_login()

st.title("Automatización")
st.caption("Configura cómo trabaja el asistente. Uso no diario.")

tabs = st.tabs(["Cómo responde", "Flow / Editor", "Branding y mensajes", "Nivel de automatización"])

with tabs[0]:
    st.subheader("Cómo responde el asistente")
    st.markdown("- Mensajes iniciales y tono")
    st.page_link("pages/05_Flujo.py", label="Abrir configuración de flujo")

with tabs[1]:
    st.subheader("Editor de flujo")
    st.page_link("pages/05_Flujo.py", label="Ir al editor de flujo")

with tabs[2]:
    st.subheader("Imagen y mensajes")
    st.page_link("pages/07_Widget.py", label="Configurar branding y widget")

with tabs[3]:
    st.subheader("Nivel de automatización")
    st.markdown(
        """
        - IA activada / Modo ahorro
        - Avisos de límite
        """
    )
