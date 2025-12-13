from pathlib import Path
from typing import Any

import streamlit as st
from quota_constants import QUOTA_COPY


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


def render_quota_banner(quota_status: str | dict | None, needs_upgrade: bool = False, upgrade_url: str | None = None):
    status = "ACTIVE"
    if isinstance(quota_status, dict):
        status = str(quota_status.get("mode") or quota_status.get("quota_status") or "ACTIVE")
        needs_upgrade = needs_upgrade or bool(quota_status.get("needs_upgrade_notice"))
    elif quota_status:
        status = str(quota_status)
    status = status.upper()
    if status == "ACTIVE":
        return
    copy = QUOTA_COPY["LOCKED"] if status == "LOCKED" else QUOTA_COPY["SAVING"]
    if status == "LOCKED":
        st.error(f"🔒 {copy['title']}: {copy['message']}")
    else:
        st.warning(f"⚠️ {copy['title']}: {copy['message']}")
    if needs_upgrade:
        if upgrade_url:
            st.markdown(f"[{copy['cta']}]({upgrade_url})", unsafe_allow_html=False)
        else:
            st.info(copy["cta"])
