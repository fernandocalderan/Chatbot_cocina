from pathlib import Path
from typing import Any

import streamlit as st


def load_styles():
    css_path = Path(__file__).parent / "styles.css"
    if css_path.exists():
        css = css_path.read_text()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def format_timestamp(value: str | None) -> str:
    if not value:
        return "-"
    return value.replace("T", " ").replace("Z", "")


def render_json(title: str, payload: Any):
    with st.expander(title, expanded=False):
        st.json(payload)
