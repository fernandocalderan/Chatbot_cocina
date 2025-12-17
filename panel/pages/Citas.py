import streamlit as st

from auth import ensure_login
from nav import legacy_redirect, nav_v2_enabled
from utils import load_styles

st.set_page_config(page_title="Citas", page_icon="📅", layout="wide")
load_styles()
ensure_login()

if nav_v2_enabled():
    legacy_redirect("/Citas", "pages/agenda.py")
else:
    legacy_redirect("/Citas", "pages/03_Agenda.py")
st.stop()
