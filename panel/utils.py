from pathlib import Path
from typing import Any

import streamlit as st
from quota_constants import QUOTA_COPY
from theme import COLORS, STATE_COLORS, FONT_FAMILY


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


def _normalize_quota(quota_status: str | dict | None) -> dict:
    if isinstance(quota_status, dict):
        return quota_status
    if quota_status:
        return {"mode": str(quota_status)}
    return {"mode": "ACTIVE"}


def render_quota_banner(quota_status: str | dict | None, needs_upgrade: bool = False, upgrade_url: str | None = None):
    qs = _normalize_quota(quota_status)
    status = "ACTIVE"
    if isinstance(qs, dict):
        status = str(qs.get("mode") or qs.get("quota_status") or "ACTIVE")
        needs_upgrade = needs_upgrade or bool(qs.get("needs_upgrade_notice"))
    status = status.upper()
    if status == "ACTIVE":
        return
    copy = QUOTA_COPY["LOCKED"] if status == "LOCKED" else QUOTA_COPY["SAVING"]
    tone = "error" if status == "LOCKED" else "warning"
    palette = STATE_COLORS.get(tone, STATE_COLORS["warning"])
    st.markdown(
        f"""
        <div style="border:1px solid {palette['fg']}33;background:{palette['bg']};color:{palette['fg']};padding:12px 14px;border-radius:10px;display:flex;justify-content:space-between;align-items:center;gap:12px;">
          <div style="display:flex;align-items:center;gap:10px;">
            <span style="font-size:18px;line-height:1;">{"🔒" if status=="LOCKED" else "⚠️"}</span>
            <div>
              <div style="font-weight:700;font-size:15px;font-family:{FONT_FAMILY};">{copy['title']}</div>
              <div style="font-size:13px;">{copy['message']}</div>
            </div>
          </div>
          <div>
            {"<a style='background:"+COLORS.get('primary')+";color:#fff;padding:8px 12px;border-radius:8px;font-weight:700;text-decoration:none;' href='"+upgrade_url+"'>"+copy['cta']+"</a>" if upgrade_url else "<span style='font-weight:700;'>"+copy['cta']+"</span>"}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_quota_usage_bar(quota_status: dict | None, label: str = "Consumo IA"):
    if not isinstance(quota_status, dict):
        return
    spent = float(quota_status.get("spent_eur") or 0.0)
    limit = quota_status.get("limit_eur")
    if limit in (None, 0, "inf"):
        return
    try:
        pct = min(max(spent / float(limit), 0), 1)
    except Exception:
        return
    st.markdown(f"**{label}: {spent:.2f} € / {float(limit):.2f} €**")
    st.progress(pct)


def metric_card(title: str, value: str, subtitle: str | None = None, accent: str = "#1E88E5"):
    st.markdown(
        f"""
        <div style="background:{COLORS.get('panel')};border:1px solid {COLORS.get('border')};border-radius:12px;padding:14px 16px;margin-bottom:12px;box-shadow:{COLORS.get('shadow')};">
          <div style="font-size:12px;color:{COLORS.get('muted')};font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">{title}</div>
          <div style="font-size:26px;font-weight:700;color:{accent};line-height:1.2;font-family:{FONT_FAMILY};">{value}</div>
          {f'<div style="font-size:13px;color:{COLORS.get('muted')};margin-top:4px;">{subtitle}</div>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def pill(text: str, tone: str = "info"):
    palette = STATE_COLORS.get(tone, STATE_COLORS["info"])
    bg, fg = palette["bg"], palette["fg"]
    return f'<span style="display:inline-block;padding:6px 12px;border-radius:999px;background:{bg};color:{fg};font-weight:700;font-size:12px;font-family:{FONT_FAMILY};">{text}</span>'
