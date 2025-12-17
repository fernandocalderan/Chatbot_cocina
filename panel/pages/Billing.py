import streamlit as st

from auth import ensure_login
from nav import legacy_redirect, nav_v2_enabled
from utils import load_styles

st.set_page_config(page_title="Billing", page_icon="💳", layout="wide")
load_styles()
ensure_login()

if nav_v2_enabled():
    st.session_state["_config_tab"] = "billing"
    legacy_redirect("/Billing", "pages/configuracion.py")
else:
    legacy_redirect("/Billing", "pages/06_Billing.py")
st.stop()
