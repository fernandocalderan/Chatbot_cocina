import streamlit as st

from api_client import get_scoring, update_scoring
from auth import ensure_login
from utils import load_styles, render_json

load_styles()
if "token" not in st.session_state:
    st.switch_page("auth.py")
ensure_login()

st.title("Scoring")

if "scoring_cfg" not in st.session_state:
    st.session_state["scoring_cfg"] = get_scoring()

scoring = st.session_state.get("scoring_cfg") or {}
weights = scoring.get("weights", {}) or {}

st.subheader("Pesos")
weights["budget"] = st.slider("Peso presupuesto", 0, 100, int(weights.get("budget", 0)))
weights["urgency"] = st.slider("Peso urgencia", 0, 100, int(weights.get("urgency", 0)))
weights["area_m2"] = st.slider("Peso área m2", 0, 100, int(weights.get("area_m2", 0)))
weights["style_defined"] = st.slider("Peso estilo definido", 0, 100, int(weights.get("style_defined", 0)))
weights["origin"] = st.slider("Peso origen", 0, 100, int(weights.get("origin", 0)))

scoring["weights"] = weights
st.session_state["scoring_cfg"] = scoring

if st.button("Guardar cambios"):
    res = update_scoring(scoring)
    if res:
        st.success("Scoring actualizado")

render_json("Config actual", scoring)
