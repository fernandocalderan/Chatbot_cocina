import streamlit as st

from auth import ensure_login
from nav import legacy_redirect_with_tab, legacy_redirect, nav_v2_enabled
from utils import load_styles

st.set_page_config(page_title="IA Usage", page_icon="🤖", layout="wide")
load_styles()
ensure_login()

if nav_v2_enabled():
    legacy_redirect_with_tab("/IA_Usage", "pages/automatizacion.py", "nivel")
else:
    legacy_redirect("/IA_Usage", "pages/04_📊_IA_Usage.py")
st.stop()
