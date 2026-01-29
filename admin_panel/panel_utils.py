from __future__ import annotations

import streamlit as st


def open_wizard(*, vertical_key: str | None = None, scope_key: str | None = None, step: int = 2) -> None:
    if vertical_key:
        st.session_state["wizard_vertical_key"] = vertical_key
    if scope_key:
        st.session_state["wizard_scope_key"] = scope_key
        st.session_state["wizard_scope_mode"] = "existing"
    if step:
        st.session_state["wizard_step"] = step
    try:
        st.switch_page("pages/08_⚡_Wizard.py")
    except Exception:
        st.page_link("pages/08_⚡_Wizard.py", label="Abrir Wizard", icon="⚡")
