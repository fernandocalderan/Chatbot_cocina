import streamlit as st

from auth import ensure_login
from nav import legacy_redirect, nav_v2_enabled
from utils import load_styles

st.set_page_config(page_title="Widget", page_icon="🧩", layout="wide")
load_styles()
ensure_login()

if nav_v2_enabled():
    st.session_state["_config_tab"] = "widget"
    legacy_redirect("/Widget", "pages/configuracion.py")
else:
    legacy_redirect("/Widget", "pages/07_Widget.py")
st.stop()
