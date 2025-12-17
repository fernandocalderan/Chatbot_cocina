import streamlit as st

from auth import ensure_login
from nav import legacy_redirect_with_tab, legacy_redirect, nav_v2_enabled
from utils import load_styles

st.set_page_config(page_title="Flujo", page_icon="🤖", layout="wide")
load_styles()
ensure_login()

if nav_v2_enabled():
    legacy_redirect_with_tab("/Flujo", "pages/automatizacion.py", "flujo")
else:
    legacy_redirect("/Flujo", "pages/05_Flujo.py")
st.stop()
