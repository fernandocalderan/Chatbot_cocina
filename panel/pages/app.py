import streamlit as st

from auth import ensure_login
from nav import legacy_redirect, nav_v2_enabled
from utils import load_styles

st.set_page_config(page_title="app", layout="wide")
load_styles()
ensure_login()

legacy_redirect("/app", "pages/inicio.py" if nav_v2_enabled() else "pages/00_Inicio.py")
st.stop()
