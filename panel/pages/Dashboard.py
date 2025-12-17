import streamlit as st

from auth import ensure_login
from nav import legacy_redirect, nav_v2_enabled
from utils import load_styles

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
load_styles()
ensure_login()

if nav_v2_enabled():
    legacy_redirect("/Dashboard", "pages/inicio.py")
else:
    legacy_redirect("/Dashboard", "pages/00_Inicio.py")
st.stop()
