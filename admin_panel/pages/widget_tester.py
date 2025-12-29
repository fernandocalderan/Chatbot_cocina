import sys
from pathlib import Path

import os
import json
import requests
import streamlit as st
import streamlit.components.v1 as components

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from admin_panel.ui import init_page, render_impersonation_banner, render_sidebar_nav, require_admin_context


init_page(title="Widget Tester", icon="🧪")

ctx = require_admin_context()
render_sidebar_nav(show_tools=False)
render_impersonation_banner()


def _api_base():
    return (
        st.session_state.get("_api_base_override")
        or os.getenv("API_BASE")
        or os.getenv("WIDGET_API_BASE")
        or "http://localhost:8100"
    )


def _widget_src():
    return (
        os.getenv("WIDGET_CDN_URL")
        or "http://localhost:5173/frontend-widget/dist/chat-widget.js"
    )


def _get_api_key():
    return st.session_state.get("_api_key") or os.getenv("ADMIN_API_TOKEN") or ""


def _request(
    method: str,
    path: str,
    *,
    api_key: str | None = None,
    token: str | None = None,
    json_body=None,
    api_base: str | None = None,
):
    base = api_base or _api_base()
    url = f"{base.rstrip('/')}{path}"
    headers: dict[str, str] = {}
    if api_key:
        headers["x-api-key"] = api_key
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        resp = requests.request(method, url, headers=headers, json=json_body, timeout=10)
        if resp.status_code >= 400:
            return {"status_code": resp.status_code, "error": resp.text}
        return resp.json()
    except Exception as exc:
        return {"status_code": 0, "error": str(exc)}


@st.cache_data(ttl=30)
def _load_tenants(api_key: str | None, token: str | None, api_base: str):
    resp = _request("GET", "/v1/admin/tenants", api_key=api_key, token=token, api_base=api_base)
    if isinstance(resp, list):
        return resp
    if isinstance(resp, dict):
        return resp.get("items") or resp.get("tenants") or []
    return []


def _issue_widget_token(api_key: str | None, token: str | None, tenant_id: str, origin: str, ttl: int):
    payload = {"allowed_origin": origin, "ttl_minutes": ttl}
    return _request(
        "POST",
        f"/v1/admin/tenants/{tenant_id}/widget-token",
        api_key=api_key,
        token=token,
        json_body=payload,
    )


st.title("Widget Tester 💬")
st.caption(
    "Genera un token, configura tenant/origen y prueba el widget (burbuja + flujo) sin salir del panel."
)

PRESETS = {
    "Auto": {},
    "Local": {
        "api_base": "http://localhost:8100",
        "widget_src": "http://localhost:5173/frontend-widget/dist/chat-widget.js",
    },
    "Staging": {
        "api_base": os.getenv("STAGING_API_BASE") or "",
        "widget_src": os.getenv("STAGING_WIDGET_CDN_URL") or "",
    },
    "Prod": {
        "api_base": os.getenv("PROD_API_BASE") or "",
        "widget_src": os.getenv("PROD_WIDGET_CDN_URL") or os.getenv("WIDGET_CDN_URL") or "",
    },
}

with st.sidebar:
    preset = st.selectbox("Preset", list(PRESETS.keys()), index=0)
    if preset != "Auto":
        cfg = PRESETS.get(preset) or {}
        if cfg.get("api_base"):
            st.session_state["_api_base_override"] = cfg["api_base"]
        if cfg.get("widget_src"):
            st.session_state["_widget_src_override"] = cfg["widget_src"]

    default_api_key = ctx.api_key or _get_api_key()
    api_key = st.text_input("API key (opcional)", value=default_api_key or "", type="password")
    st.session_state["_api_key"] = api_key
    api_base = st.text_input("API base", value=_api_base())
    st.session_state["_api_base_override"] = api_base
    widget_src = st.text_input(
        "Widget JS (CDN/local)",
        value=(st.session_state.get("_widget_src_override") or _widget_src()),
        help="Orden recomendado: CDN o build local (frontend-widget/dist/chat-widget.js).",
    )

if not api_key and not ctx.token:
    st.warning("Introduce un API key o inicia sesión con OIDC para continuar.")
    st.stop()

with st.spinner("Cargando tenants…"):
    tenants = _load_tenants(api_key or None, ctx.token, api_base)
if not tenants:
    st.error("No se pudieron cargar tenants. Revisa API base/API key.")
    st.stop()

tenant_map = {t["name"] or t["id"]: t for t in tenants}
selected_name = st.selectbox("Selecciona tenant", options=list(tenant_map.keys()))
tenant = tenant_map[selected_name]

col_info, col_token = st.columns([0.5, 0.5])
with col_info:
    st.markdown(f"**Tenant ID:** `{tenant['id']}`")
    st.markdown(f"**Vertical:** `{tenant.get('vertical_key') or 'N/D'}`")
    allowed = tenant.get("allowed_origins") or []
    st.markdown(f"**Allowed origins:** {', '.join(allowed) if allowed else 'ninguno'}")

with col_token:
    # El widget se ejecuta dentro de un iframe del propio panel (origen = host:puerto de Streamlit).
    panel_port = st.get_option("server.port") or 8501
    panel_origin_default = f"http://localhost:{panel_port}"
    origin = st.text_input(
        "Dominio permitido (allowed_origin del token)",
        value=(allowed[0] if allowed else panel_origin_default),
        help="En este panel, el widget corre bajo el origen del admin panel (normalmente http://localhost:8501).",
    )
    ttl = st.slider("TTL minutos", min_value=15, max_value=60, value=60, step=15)
    token_state_key = f"_widget_token_{tenant['id']}"
    token_input = st.text_area(
        "Token widget (pegar uno existente)",
        value=st.session_state.get(token_state_key) or "",
        height=80,
        key="widget_token_area",
    )
    if st.button("Generar token nuevo", use_container_width=True):
        res = _issue_widget_token(api_key or None, ctx.token, tenant["id"], origin, ttl)
        if isinstance(res, dict) and res.get("token"):
            token_input = res["token"]
            st.session_state[token_state_key] = token_input
            st.success("Token generado.")
        else:
            st.error(res)

    allowed_origins = tenant.get("allowed_origins") or []
    if origin and origin not in allowed_origins:
        st.warning("El origen no está en `allowed_origins` del tenant. El widget puede fallar por CORS.")
        if st.button("Añadir origen al tenant", use_container_width=True):
            new_list = list(dict.fromkeys([*allowed_origins, origin]))
            upd = _request(
                "PATCH",
                f"/v1/admin/tenants/{tenant['id']}",
                api_key=api_key or None,
                token=ctx.token,
                json_body={"allowed_origins": new_list},
                api_base=api_base,
            )
            if isinstance(upd, dict) and upd.get("error"):
                st.error(upd)
            else:
                st.success("Origen añadido. Recarga tenants para ver el cambio.")
                st.cache_data.clear()

if not token_input:
    st.info("Genera o pega un token para probar el widget.")
    st.stop()

# Persistir token limpio en sesión
token_input = token_input.strip()
if token_input:
    st.session_state[token_state_key] = token_input

st.divider()
st.subheader("Widget en vivo")
st.caption("Se monta el widget real con el token/tenant indicados.")

# Cache-bust: evita servir un JS cacheado por el navegador al cambiar builds
widget_src_effective = widget_src.strip()
if widget_src_effective:
    sep = "&" if "?" in widget_src_effective else "?"
    widget_src_effective = f"{widget_src_effective}{sep}v={abs(hash(widget_src_effective))%100000}-{abs(hash(token_input))%100000}"

html = f"""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <style>
      body {{
        margin: 0;
        padding: 0;
        font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
      }}
      #root {{
        min-height: 600px;
      }}
    </style>
  </head>
  <body>
    <div id="widget-root"></div>
    <script>
      // Limpia cache local para evitar tokens antiguos en pruebas
      try {{
        window.localStorage.removeItem("widget_token");
      }} catch (e) {{}}
    </script>
    <script src="{widget_src_effective}" async
      data-api="{api_base}"
      data-tenant="{tenant['id']}"
      data-token="{token_input}"
      data-start-open="true">
    </script>
  </body>
</html>
"""
components.html(html, height=720, scrolling=True)
