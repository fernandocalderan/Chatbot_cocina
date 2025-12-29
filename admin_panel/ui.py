from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import streamlit as st

from admin_panel.api_client import admin_login, list_verticals, resolve_admin_api_key
from admin_panel.theme import COLORS, STATE_COLORS


@dataclass(frozen=True)
class AdminContext:
    token: str | None
    api_key: str | None
    email: str | None
    roles: tuple[str, ...]

    @property
    def is_super_admin(self) -> bool:
        return "SUPER_ADMIN" in self.roles


def init_page(*, title: str, icon: str | None = None) -> None:
    st.set_page_config(page_title=title, page_icon=icon, layout="wide")
    _load_styles()


def _load_styles() -> None:
    css_path = Path(__file__).parent / "styles.css"
    if css_path.exists():
        css = css_path.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def _decode_jwt_no_verify(token: str) -> dict[str, Any]:
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return {}
        payload_b64 = parts[1]
        payload_b64 += "=" * (-len(payload_b64) % 4)
        raw = base64.urlsafe_b64decode(payload_b64.encode("utf-8")).decode("utf-8")
        return json.loads(raw) if raw else {}
    except Exception:
        return {}


def require_admin_context() -> AdminContext:
    """
    Renderiza el login en sidebar (OIDC o API key) y devuelve el contexto (token/api_key/roles).
    Si no hay credenciales, hace st.stop().
    """
    admin_api_key = resolve_admin_api_key()
    with st.sidebar:
        st.markdown("### Acceso")
        if admin_api_key:
            st.success("Autenticado con `ADMIN_API_KEY/ADMIN_API_TOKEN` (bypass OIDC).")
            st.session_state["admin_token"] = None
            st.session_state["admin_api_key"] = admin_api_key
            st.session_state["admin_email"] = None
            st.session_state["admin_roles"] = ["SUPER_ADMIN"]
        else:
            st.caption("Pega el ID token del IdP (OIDC) autorizado.")
            oidc_token = st.text_area("ID Token OIDC", height=140)
            if st.button("Iniciar sesión", use_container_width=True):
                try:
                    resp = admin_login(oidc_token)
                    if resp and (resp.get("token") or resp.get("api_key")):
                        st.session_state["admin_token"] = resp.get("token")
                        st.session_state["admin_api_key"] = resp.get("api_key")
                        st.session_state["admin_email"] = resp.get("email")
                        roles = []
                        if resp.get("token"):
                            claims = _decode_jwt_no_verify(resp["token"])
                            roles = claims.get("roles") or []
                        st.session_state["admin_roles"] = roles or ["SUPER_ADMIN"]
                        st.success(f"Autenticado: {resp.get('email') or 'api_key'}")
                    else:
                        st.error("No se pudo iniciar sesión")
                except Exception as exc:
                    st.error(f"Error: {exc}")

    token = st.session_state.get("admin_token")
    api_key = st.session_state.get("admin_api_key") or admin_api_key
    if not token and not api_key:
        st.stop()

    email = st.session_state.get("admin_email")
    roles_raw = st.session_state.get("admin_roles") or []
    roles = tuple(str(r) for r in roles_raw if r)
    return AdminContext(token=token, api_key=api_key, email=email, roles=roles)


def render_sidebar_nav(*, show_tools: bool = True) -> None:
    with st.sidebar:
        st.markdown("### SuperAdmin")
        st.page_link("app.py", label="Inicio", icon="🏠")
        st.page_link("pages/01_📊_Overview.py", label="Overview", icon="📊")
        st.page_link("pages/02_🏢_Tenants.py", label="Tenants", icon="🏢")
        st.page_link("pages/03_🧩_Verticals.py", label="Verticals", icon="🧩")
        st.page_link("pages/04_➕_Crear_tenant.py", label="Crear tenant", icon="➕")
        st.page_link("pages/05_🧾_Auditoría.py", label="Auditoría", icon="🧾")
        if show_tools:
            st.markdown("---")
            st.page_link("pages/widget_tester.py", label="Widget tester", icon="🧪")


def render_impersonation_banner() -> None:
    impersonation_token = st.session_state.get("impersonation_token")
    if not impersonation_token:
        return
    with st.container():
        st.markdown(
            """
            <div style="padding:12px;border:1px solid #f44336;background:#ffebee;border-radius:6px;margin-bottom:12px;">
            <strong>Modo impersonación activo:</strong> estás operando como TENANT. Sal del modo impersonación antes de realizar otras acciones.
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Salir de impersonación"):
            st.session_state.pop("impersonation_token", None)
            st.rerun()


def ensure_vertical_catalog(
    ctx: AdminContext,
) -> tuple[list[dict[str, Any]], list[str], dict[str, str], dict[str, dict[str, Any]]]:
    cache_key = "_admin_vertical_catalog"
    cached = st.session_state.get(cache_key)
    if isinstance(cached, dict) and isinstance(cached.get("items"), list):
        items = cached["items"]
    else:
        payload = list_verticals(ctx.token, api_key=ctx.api_key) or {}
        items_raw = payload.get("items") or []
        items = [v for v in items_raw if isinstance(v, dict) and v.get("key")]
        items = sorted(items, key=lambda v: str(v.get("label") or v.get("key") or "").lower())
        st.session_state[cache_key] = {"items": items}
    keys = [v.get("key") for v in items if v.get("key")]
    labels = {v.get("key"): v.get("label") for v in items if v.get("key")}
    by_key = {v.get("key"): v for v in items if v.get("key")}
    return items, keys, labels, by_key


def can_write(ctx: AdminContext) -> bool:
    if str(os.getenv("ADMIN_PANEL_READONLY") or "").strip().lower() in {"1", "true", "yes", "on"}:
        return False
    return ctx.is_super_admin


def metric_card(title: str, value: str, subtitle: str | None = None, accent: str | None = None) -> None:
    accent_color = accent or COLORS.get("primary") or "#1E88E5"
    st.markdown(
        f"""
        <div class="op-card" style="margin-bottom:12px;">
          <div class="op-card-kicker">{title}</div>
          <div class="op-card-value" style="color:{accent_color};">{value}</div>
          {f'<div class="op-card-subtitle">{subtitle}</div>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def pill(text: str, tone: str = "info") -> str:
    tone_norm = (tone or "info").lower()
    if tone_norm == "error":
        tone_norm = "danger"
    if tone_norm not in {"success", "warning", "danger", "info"}:
        tone_norm = "info"
    palette = STATE_COLORS.get(tone_norm, STATE_COLORS["info"])
    return f'<span class="op-pill op-pill--{tone_norm}" style="background:{palette["bg"]};color:{palette["fg"]};">{text}</span>'
