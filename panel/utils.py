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
    tone = "danger" if status == "LOCKED" else "warning"
    palette = STATE_COLORS.get(tone, STATE_COLORS["warning"])
    st.markdown(
        f"""
        <div class="op-card" style="border-left:4px solid {palette['fg']};background:{palette['bg']};">
          <div style="display:flex;justify-content:space-between;align-items:center;gap:14px;">
            <div style="display:flex;align-items:flex-start;gap:10px;">
              <div style="font-size:18px;line-height:1;margin-top:2px;">{"🔒" if status=="LOCKED" else "⚠️"}</div>
              <div>
                <div style="font-weight:600;font-size:14px;">{copy['title']}</div>
                <div style="font-size:13px;color:{COLORS.get('text')};opacity:0.9;">{copy['message']}</div>
              </div>
            </div>
            <div>
              {"<a class='op-btn op-btn-primary' style='background:"+COLORS.get('primary')+";color:#fff;padding:10px 12px;border-radius:10px;font-weight:600;text-decoration:none;display:inline-block;' href='"+upgrade_url+"'>"+copy['cta']+"</a>" if upgrade_url else "<span style='font-weight:600;'>"+copy['cta']+"</span>"}
            </div>
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
        <div class="op-card" style="margin-bottom:12px;">
          <div class="op-card-kicker">{title}</div>
          <div class="op-card-value" style="color:{accent};">{value}</div>
          {f'<div class="op-card-subtitle">{subtitle}</div>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def pill(text: str, tone: str = "info"):
    tone_norm = (tone or "info").lower()
    if tone_norm == "error":
        tone_norm = "danger"
    if tone_norm not in {"success", "warning", "danger", "info"}:
        tone_norm = "info"
    palette = STATE_COLORS.get(tone_norm, STATE_COLORS["info"])
    # Mantén colores del DS aunque Streamlit no aplique clases en todos los lugares.
    return f'<span class="op-pill op-pill--{tone_norm}" style="background:{palette["bg"]};color:{palette["fg"]};">{text}</span>'


def empty_state(title: str, message: str, icon: str = "✨"):
    st.markdown(
        f"""
        <div class="op-card" style="text-align:left;">
          <div style="display:flex;gap:12px;align-items:flex-start;">
            <div style="font-size:20px;line-height:1;">{icon}</div>
            <div>
              <div style="font-weight:600;margin-bottom:2px;">{title}</div>
              <div style="color:{COLORS.get('muted')};font-size:13px;">{message}</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def loading_state(message: str = "Estamos cargando la información. El asistente sigue activo."):
    st.info(message)
    st.markdown('<div class="op-skeleton-line"></div>', unsafe_allow_html=True)
    st.markdown('<div class="op-skeleton-line" style="width:85%;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="op-skeleton-line" style="width:70%;"></div>', unsafe_allow_html=True)
