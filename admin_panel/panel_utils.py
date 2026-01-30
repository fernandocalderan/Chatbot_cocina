from __future__ import annotations

import streamlit as st


def open_wizard(*, vertical_key: str | None = None, scope_key: str | None = None, step: int = 2) -> None:
    if vertical_key:
        st.session_state["wiz_vertical_key"] = vertical_key
        st.session_state["wizard_vertical_key"] = vertical_key
    if scope_key:
        st.session_state["wiz_scope_key"] = scope_key
        st.session_state["wizard_scope_key"] = scope_key
        st.session_state["wizard_scope_mode"] = "existing"
    if step:
        st.session_state["wiz_step"] = step
        st.session_state["wizard_step"] = step
    try:
        st.switch_page("pages/08_⚡_Wizard.py")
    except Exception:
        st.page_link("pages/08_⚡_Wizard.py", label="Abrir Wizard", icon="⚡")


def open_verticals(
    *,
    vertical_key: str | None = None,
    scope_key: str | None = None,
    tab: str | None = None,
) -> None:
    payload: dict[str, str] = {}
    if vertical_key:
        payload["vertical_key"] = vertical_key
    if scope_key:
        payload["scope_key"] = scope_key
    if tab:
        payload["tab"] = tab
    if payload:
        st.session_state["open_verticals"] = payload
    try:
        st.switch_page("pages/03_🧩_Verticals.py")
    except Exception:
        st.page_link("pages/03_🧩_Verticals.py", label="Abrir Verticals", icon="🧩")
