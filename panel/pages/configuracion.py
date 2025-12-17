from __future__ import annotations

import json
import os
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components

from auth import ensure_login
from nav import render_sidebar, show_flash, nav_v2_enabled
from api_client import (
    get_billing,
    get_tenant_config,
    issue_widget_token,
    api_set_password,
    get_widget_settings,
    update_widget_settings,
    update_tenant_config,
)
from theme import COLORS, STATE_COLORS
from utils import load_styles, empty_state, metric_card, render_quota_banner, pill

st.set_page_config(page_title="Configuración", page_icon="⚙️", layout="wide")
load_styles()
ensure_login(allow_when_must_set_password=True)
if not nav_v2_enabled() and not st.session_state.get("must_set_password"):
    st.switch_page("pages/05_Configuracion.py")
    st.stop()
render_sidebar()

show_flash()

st.title("Configuración")
st.caption("Zona administrativa: ordenada, segura y sin ruido.")

_SEC_KEY_TO_LABEL = {
    "billing": "Plan y facturación",
    "widget": "Instalación del widget",
    "seguridad": "Seguridad y accesos",
    "preferencias": "Preferencias del negocio",
}
_SEC_LABEL_TO_KEY = {v: k for k, v in _SEC_KEY_TO_LABEL.items()}


def _qp_get(key: str) -> str | None:
    try:
        value = st.query_params.get(key)
        if isinstance(value, list):
            value = value[0] if value else None
        return str(value) if value else None
    except Exception:
        return None


def _qp_set(key: str, value: str):
    try:
        st.query_params[key] = value
    except Exception:
        pass


def _sync_subroute_from_path():
    # Nota: no usamos subrutas tipo /configuracion/widget porque rompen assets de Streamlit.
    return


def _clean_url(sec_key: str):
    # Mantener query params (no tocar pathname).
    return


def _mask_secret(value: str, keep_end: int = 6) -> str:
    v = (value or "").strip()
    if not v:
        return "—"
    if len(v) <= keep_end + 4:
        return "••••••"
    return "••••••••••••" + v[-keep_end:]


def _human_billing_status(raw: str) -> tuple[str, str]:
    s = (raw or "").upper()
    if s == "ACTIVE":
        return ("Activo", "success")
    if s == "SAVING":
        return ("Ahorro", "warning")
    if s == "LOCKED":
        return ("Bloqueado", "danger")
    if s:
        return (s.title(), "info")
    return ("—", "info")


def _human_date(value: str | None) -> str:
    if not value:
        return "—"
    try:
        v = str(value).replace("Z", "+00:00")
        dt = datetime.fromisoformat(v)
        return dt.date().strftime("%d/%m/%Y")
    except Exception:
        return "—"


def _copy_snippet(snippet: str, key: str):
    text_js = json.dumps(snippet or "")
    components.html(
        f"""
        <div style="display:flex;gap:10px;align-items:center;margin:8px 0 0;">
          <button id="op-copy-{key}" class="op-btn op-btn-secondary" style="cursor:pointer;">Copiar</button>
          <span id="op-copy-msg-{key}" style="font-size:12px;opacity:.75;"></span>
        </div>
        <script>
        (function() {{
          const btn = document.getElementById("op-copy-{key}");
          const msg = document.getElementById("op-copy-msg-{key}");
          const text = {text_js};
          if (!btn) return;
          btn.addEventListener("click", async () => {{
            try {{
              await navigator.clipboard.writeText(text);
              if (msg) msg.textContent = "Copiado";
              setTimeout(() => {{ if (msg) msg.textContent = ""; }}, 1200);
            }} catch (e) {{
              try {{
                const ta = document.createElement("textarea");
                ta.value = text;
                ta.style.position = "fixed";
                ta.style.left = "-9999px";
                document.body.appendChild(ta);
                ta.select();
                document.execCommand("copy");
                document.body.removeChild(ta);
                if (msg) msg.textContent = "Copiado";
                setTimeout(() => {{ if (msg) msg.textContent = ""; }}, 1200);
              }} catch (e2) {{}}
            }}
          }});
        }})();
        </script>
        """,
        height=52,
    )


_sync_subroute_from_path()

force_security = bool(st.session_state.get("must_set_password"))
sec_key = (_qp_get("sec") or st.session_state.get("_config_tab") or "billing").lower()
if sec_key not in _SEC_KEY_TO_LABEL:
    sec_key = "billing"
if force_security:
    sec_key = "seguridad"
st.session_state["_config_tab"] = sec_key

radio_options = list(_SEC_KEY_TO_LABEL.values())
if force_security:
    radio_options = [_SEC_KEY_TO_LABEL["seguridad"]]
    st.info("Activa tu cuenta para continuar. Solo Seguridad está disponible ahora.")

sec_label = st.radio(
    "Configuración",
    options=radio_options,
    index=0 if force_security else list(_SEC_KEY_TO_LABEL.keys()).index(sec_key),
    horizontal=True,
    label_visibility="collapsed",
)
selected_key = _SEC_LABEL_TO_KEY.get(sec_label, "billing")
if selected_key != sec_key:
    st.session_state["_config_tab"] = selected_key
    _qp_set("sec", selected_key)
    st.rerun()

st.caption(f"Configuración > {_SEC_KEY_TO_LABEL[selected_key]}")

if selected_key == "billing":
    st.subheader("Plan y facturación")
    st.caption("Plan actual, estado y acceso al portal de facturación.")

    with st.spinner("Cargando…"):
        billing = get_billing() or {}
    if not isinstance(billing, dict) or not billing or billing.get("status_code"):
        empty_state("No pudimos cargar la facturación", "Estamos cargando la información. El asistente sigue activo.", icon="⚠️")
    else:
        plan = (billing.get("plan") or "N/D").upper()
        raw_status = (billing.get("billing_status") or billing.get("stripe_status") or "")
        status_h, status_tone = _human_billing_status(str(raw_status))
        renewal = _human_date(billing.get("current_period_end"))
        quota_status = billing.get("quota_status")
        needs_upgrade = bool(quota_status.get("needs_upgrade_notice")) if isinstance(quota_status, dict) else False

        render_quota_banner(quota_status, needs_upgrade=needs_upgrade, upgrade_url=billing.get("manage_url"))

        c1, c2, c3 = st.columns(3)
        with c1:
            metric_card("Plan", plan, subtitle="Nivel actual", accent=COLORS["text"])
        with c2:
            metric_card("Estado", status_h, subtitle="Suscripción", accent=STATE_COLORS.get(status_tone, STATE_COLORS["info"])["fg"])
        with c3:
            metric_card("Renovación", renewal, subtitle="Próximo ciclo", accent=COLORS["primary"])

        portal = billing.get("manage_url")
        if portal:
            st.link_button("Abrir portal", portal, use_container_width=True)
        else:
            st.caption("Portal no disponible ahora.")

        if needs_upgrade:
            st.markdown(pill("Requiere upgrade", tone="warning"), unsafe_allow_html=True)
        else:
            st.markdown(pill("Todo en orden", tone="success"), unsafe_allow_html=True)

elif selected_key == "widget":
    st.subheader("Instalación del widget")
    st.caption("Pega el snippet en tu web antes de `</body>`.")

    cfg = get_tenant_config() or {}
    if isinstance(cfg, dict) and cfg.get("status_code"):
        empty_state("No pudimos cargar la configuración", "Estamos cargando la información. El asistente sigue activo.", icon="⚠️")
    else:
        tenant_id = st.session_state.get("tenant_id") or cfg.get("tenant_id") or os.getenv("PANEL_TENANT_ID", "<TENANT_ID>")
        api_base = os.getenv("WIDGET_API_BASE", os.getenv("API_BASE", "https://api.opunnence.com"))
        cdn_url = os.getenv("WIDGET_CDN_URL", "https://cdn.opunnence.com/widget.js")

        # Dominios permitidos (allowlist) — si existe en backend.
        settings = get_widget_settings() or {}
        allowed_list = []
        if isinstance(settings, dict) and isinstance(settings.get("allowed_origins"), list):
            allowed_list = [str(o) for o in settings.get("allowed_origins") if o]

        default_origin = os.getenv("WIDGET_ALLOWED_ORIGIN", "https://tu-dominio.com")
        col1, col2 = st.columns(2)
        with col1:
            if allowed_list:
                allowed_origin = st.selectbox("Dominio permitido", options=allowed_list, index=0)
                st.caption("Estos dominios ya están autorizados para tu widget.")
                new_origin = st.text_input("Añadir dominio", value="", placeholder="https://tu-dominio.com")
                if new_origin:
                    c = st.columns([0.6, 0.4])
                    with c[0]:
                        confirm_add = st.checkbox("Confirmo autorizar este dominio", value=False, key="confirm_add_origin")
                    with c[1]:
                        if st.button("Autorizar", use_container_width=True, disabled=not confirm_add, key="authorize_origin"):
                            out = update_widget_settings(sorted(set(allowed_list + [str(new_origin)]))) or {}
                            if isinstance(out, dict) and out.get("status_code"):
                                empty_state("No pudimos autorizar ahora", "Contacta soporte para habilitar dominios.", icon="⚠️")
                            else:
                                st.success("Dominio autorizado.")
                                st.rerun()
            else:
                allowed_origin = st.text_input("Dominio permitido", value=default_origin, help="Ej: https://tu-dominio.com")
        with col2:
            ttl = st.slider("TTL (min)", min_value=15, max_value=60, value=30, step=5)

        if st.button("Generar token", use_container_width=True):
            with st.spinner("Creando…"):
                resp = issue_widget_token(allowed_origin, ttl_minutes=int(ttl))
            if resp and isinstance(resp, dict) and resp.get("token"):
                st.session_state["_widget_token_data"] = resp
                st.success("Token generado.")
                st.rerun()
            elif isinstance(resp, dict) and resp.get("status_code") == 403:
                detail = resp.get("detail")
                d = detail.get("detail") if isinstance(detail, dict) else detail
                if str(d) == "origin_not_allowed":
                    empty_state(
                        "Dominio no autorizado",
                        "Añádelo a los dominios permitidos y vuelve a generar el token.",
                        icon="🔒",
                    )
                    c = st.columns([0.6, 0.4])
                    with c[0]:
                        confirm = st.checkbox("Confirmo autorizar este dominio", value=False)
                    with c[1]:
                        if st.button("Autorizar", use_container_width=True, disabled=not confirm):
                            new_list = sorted(set((allowed_list or []) + [str(allowed_origin)]))
                            out = update_widget_settings(new_list) or {}
                            if isinstance(out, dict) and out.get("status_code"):
                                empty_state("No pudimos autorizar ahora", "Contacta soporte para habilitar dominios.", icon="⚠️")
                            else:
                                st.success("Dominio autorizado.")
                                st.rerun()
                else:
                    empty_state("No pudimos generar el token", "Revisa tus permisos para el widget.", icon="⚠️")
            else:
                empty_state("No pudimos generar el token", "Estamos cargando la información. El asistente sigue activo.", icon="⚠️")

        token_data = st.session_state.get("_widget_token_data")
        if token_data and isinstance(token_data, dict) and token_data.get("token"):
            snippet = f"""<div id="widget-root"></div>
<script src="{cdn_url}" async
  data-api="{api_base}"
  data-tenant="{tenant_id}"
  data-token="{token_data.get("token")}"
  data-start-open="false">
</script>"""
            st.code(snippet, language="html")
            _copy_snippet(snippet, key="widget")
            st.caption('Tip: usa `data-start-open="true"` si quieres que se abra automáticamente.')
        else:
            empty_state("Aún no hay snippet", "Genera un token para obtener el código listo para copiar.", icon="🧩")

elif selected_key == "seguridad":
    st.subheader("Seguridad y accesos")
    st.caption("Accesos, credenciales y acciones críticas.")

    token = st.session_state.get("token") or st.session_state.get("access_token") or ""
    must_set_password = bool(st.session_state.get("must_set_password"))
    st.markdown("### Sesión")
    st.markdown(pill("Activa" if token else "Sin sesión", tone="success" if token else "warning"), unsafe_allow_html=True)
    st.text_input("Token (oculto)", value=_mask_secret(str(token)), disabled=True)

    st.divider()
    if must_set_password:
        st.markdown("### Activar cuenta")
        st.caption("Crea tu contraseña para desbloquear el panel.")
        with st.form("set_pwd", clear_on_submit=True):
            pwd = st.text_input("Nueva contraseña", type="password")
            pwd2 = st.text_input("Confirmar contraseña", type="password")
            confirm = st.checkbox("Confirmo que quiero activar mi cuenta")
            submitted = st.form_submit_button("Guardar", use_container_width=True)
        if submitted:
            if not confirm:
                st.info("Confirma la acción para continuar.")
            elif not pwd or not pwd2:
                st.info("Completa ambos campos.")
            else:
                with st.spinner("Guardando…"):
                    resp = api_set_password(pwd, pwd2)
                if resp and isinstance(resp, dict) and resp.get("status") == "ok" and resp.get("token"):
                    st.session_state["must_set_password"] = False
                    st.session_state["token"] = resp["token"]
                    st.session_state["access_token"] = resp["token"]
                    st.success("Cuenta activada.")
                    st.switch_page("pages/inicio.py")
                else:
                    empty_state("No pudimos activar ahora", "Revisa el enlace recibido por email o contacta soporte.", icon="⚠️")
    else:
        st.markdown("### Contraseña")
        st.caption("Para cambiar tu contraseña, contacta soporte o solicita un nuevo enlace de acceso.")

    st.divider()
    st.markdown("### Cerrar sesión")
    c = st.columns([0.6, 0.4])
    with c[0]:
        logout_confirm = st.checkbox("Confirmo que quiero cerrar sesión", value=False)
    with c[1]:
        if st.button("Salir", use_container_width=True, disabled=not logout_confirm):
            for k in ["token", "access_token", "must_set_password", "must_set_password_required"]:
                st.session_state.pop(k, None)
            st.success("Sesión cerrada.")
            st.switch_page("pages/auth.py")

elif selected_key == "preferencias":
    st.subheader("Preferencias del negocio")
    st.caption("Ajustes operativos simples (idioma, zona horaria, moneda).")

    cfg = get_tenant_config() or {}
    name = st.session_state.get("tenant_name") or (cfg.get("name") if isinstance(cfg, dict) else None) or "Tu negocio"
    current_lang = str(st.session_state.get("tenant_language") or (cfg.get("language") if isinstance(cfg, dict) else None) or "es").lower()
    current_tz = str(st.session_state.get("tenant_timezone") or (cfg.get("timezone") if isinstance(cfg, dict) else None) or "Europe/Madrid")
    current_currency = str(st.session_state.get("tenant_currency") or (cfg.get("currency") if isinstance(cfg, dict) else None) or "EUR").upper()

    st.text_input("Nombre comercial", value=str(name), disabled=True)

    with st.form("prefs"):
        c1, c2, c3 = st.columns(3)
        lang = c1.selectbox("Idioma", options=["es", "pt", "en", "ca"], index=max(0, ["es", "pt", "en", "ca"].index(current_lang) if current_lang in ["es", "pt", "en", "ca"] else 0))
        tz = c2.text_input("Zona horaria", value=current_tz, help="Ej: Europe/Madrid")
        currency = c3.selectbox("Moneda", options=["EUR", "BRL", "USD"], index=max(0, ["EUR", "BRL", "USD"].index(current_currency) if current_currency in ["EUR", "BRL", "USD"] else 0))
        saved = st.form_submit_button("Guardar", use_container_width=True)
    if saved:
        out = update_tenant_config(language=lang, timezone=tz, currency=currency) or {}
        if isinstance(out, dict) and out.get("status_code"):
            # fallback local (no rompe operación)
            st.session_state["tenant_language"] = lang
            st.session_state["tenant_timezone"] = tz
            st.session_state["tenant_currency"] = currency
            st.success("Guardado.")
            st.caption("Aplicado en esta sesión. Para guardar de forma permanente, contacta soporte.")
        else:
            st.session_state["tenant_language"] = out.get("language") or lang
            st.session_state["tenant_timezone"] = out.get("timezone") or tz
            st.session_state["tenant_currency"] = out.get("currency") or currency
            st.success("Guardado.")
            st.rerun()
