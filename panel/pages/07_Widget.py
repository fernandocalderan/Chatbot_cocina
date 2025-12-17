import streamlit as st

from auth import ensure_login
from nav import legacy_redirect
from utils import load_styles

load_styles()
ensure_login()
st.session_state["_config_tab"] = "widget"
legacy_redirect("/Widget", "pages/configuracion.py")
st.stop()
