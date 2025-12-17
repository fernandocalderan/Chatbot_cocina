import streamlit as st

from auth import ensure_login
from nav import legacy_redirect, nav_v2_enabled
from utils import load_styles

st.set_page_config(page_title="Leads", page_icon="📈", layout="wide")
load_styles()
ensure_login()

if nav_v2_enabled():
    legacy_redirect("/Leads", "pages/oportunidades.py")
else:
    legacy_redirect("/Leads", "pages/02_Oportunidades.py")
st.stop()
