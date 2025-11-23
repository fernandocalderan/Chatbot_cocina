import streamlit as st

from api_client import login
from utils import load_styles

load_styles()
st.title("Login")

email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Login"):
    token = login(email, password)
    if token:
        st.session_state["token"] = token
        st.session_state["access_token"] = token  # compat con cliente existente
        st.success("Autenticación correcta")
        st.switch_page("app.py")
