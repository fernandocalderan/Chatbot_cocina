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
        # Local default: use repo build (sin servidor).
        or "local:frontend-widget/dist/chat-widget.js"
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


def _get_tenant_flow_info(api_key: str | None, token: str | None, tenant_id: str, api_base: str):
    return _request("GET", f"/v1/admin/tenants/{tenant_id}/flow", api_key=api_key, token=token, api_base=api_base)


st.title("Widget Tester 💬")
st.caption(
    "Genera un token, configura tenant/origen y prueba el widget (burbuja + flujo) sin salir del panel."
)

PRESETS = {
    "Auto": {},
    "Local": {
        "api_base": "http://localhost:8100",
        "widget_src": "local:frontend-widget/dist/chat-widget.js",
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

tenant_map = {t["name"] or t["id"]: t for t in tenants if isinstance(t, dict) and t.get("id")}
names = list(tenant_map.keys())
selected_idx = 0
try:
    state_tid = st.session_state.get("_widget_tester_tenant_id")
    if state_tid:
        for i, n in enumerate(names):
            if str(tenant_map[n].get("id")) == str(state_tid):
                selected_idx = i
                break
    qp_tid = st.query_params.get("tenant_id")
    if isinstance(qp_tid, list):
        qp_tid = qp_tid[0] if qp_tid else None
    if qp_tid:
        for i, n in enumerate(names):
            if str(tenant_map[n].get("id")) == str(qp_tid):
                selected_idx = i
                break
except Exception:
    selected_idx = 0

selected_name = st.selectbox("Selecciona tenant", options=names, index=selected_idx)
tenant = tenant_map[selected_name]

col_info, col_token = st.columns([0.5, 0.5])
with col_info:
    st.markdown(f"**Tenant ID:** `{tenant['id']}`")
    st.markdown(f"**Vertical:** `{tenant.get('vertical_key') or 'N/D'}`")
    allowed = tenant.get("allowed_origins") or []
    st.markdown(f"**Allowed origins:** {', '.join(allowed) if allowed else 'ninguno'}")
    st.markdown("**Flow efectivo (qué se está probando):**")
    flow_info = _get_tenant_flow_info(api_key or None, ctx.token, tenant["id"], api_base)
    if isinstance(flow_info, dict) and flow_info.get("error"):
        st.error(flow_info)
    elif isinstance(flow_info, dict):
        flow_system = str(flow_info.get("flow_system") or "v2").lower()
        published = flow_info.get("published") if isinstance(flow_info.get("published"), dict) else None
        scopes = flow_info.get("scopes") or []
        if flow_system == "v2" and published:
            st.success(f"Published v{published.get('version')} · {published.get('flow_id')}")
        else:
            st.info(f"Fallback a base scope: {scopes[0] if scopes else '—'}")
        eff = flow_info.get("effective_flow") if isinstance(flow_info.get("effective_flow"), dict) else {}
        blocks = eff.get("blocks") if isinstance(eff.get("blocks"), dict) else {}
        st.caption(f"start_block: `{eff.get('start_block') or '—'}` · blocks: {len(blocks)}")
        with st.expander("Ver JSON efectivo", expanded=False):
            st.json(eff or {})

with col_token:
    # El widget se ejecuta dentro de un iframe del propio panel (origen = host:puerto de Streamlit).
    panel_port = st.get_option("server.port") or 8502
    panel_addr = st.get_option("server.address") or "localhost"
    # Si el servidor escucha 0.0.0.0, el navegador puede estar en localhost o 0.0.0.0.
    # Por defecto usamos el address configurado para minimizar errores (captura el caso 0.0.0.0).
    panel_origin_default = f"http://{panel_addr}:{panel_port}"
    panel_origin_alt = None
    if panel_addr not in {"localhost", "127.0.0.1", "0.0.0.0"}:
        panel_origin_alt = f"http://localhost:{panel_port}"
    elif panel_addr != "localhost":
        panel_origin_alt = f"http://localhost:{panel_port}"
    mode = st.radio(
        "Modo de prueba",
        ["Dentro del panel (iframe)", "Página externa"],
        index=0,
        horizontal=True,
        help="Dentro del panel: el widget corre bajo el origen del admin panel (ej. http://localhost:8502). "
        "Página externa: úsalo para probar en http://localhost:3000 u otros dominios.",
    )
    if mode.startswith("Dentro"):
        origin = panel_origin_default
        st.text_input("Dominio permitido (allowed_origin del token)", value=origin, disabled=True)
        if panel_origin_alt and panel_origin_alt != origin:
            st.caption(f"Si abriste este panel con otro host, prueba también `{panel_origin_alt}`.")
    else:
        origin = st.text_input(
            "Dominio permitido (allowed_origin del token)",
            value=(tenant.get("allowed_origins") or ["http://localhost:3000"])[0],
            help="Este debe coincidir con el `Origin` real del sitio donde cargas el widget.",
        )
        st.caption("Tip: para probar en local, abre `test-widget.html` o tu frontend en `http://localhost:3000`.")
    ttl = st.slider("TTL minutos", min_value=15, max_value=60, value=60, step=15)
    token_state_key = f"_widget_token_{tenant['id']}"
    token_input = st.text_area(
        "Token widget (pegar uno existente)",
        value=st.session_state.get(token_state_key) or "",
        height=80,
        key="widget_token_area",
    )
    if st.button("Generar token nuevo", use_container_width=True):
        # Si el origin no está permitido en el tenant, lo añadimos primero para evitar 403.
        allowed_origins = tenant.get("allowed_origins") or []
        if origin and origin not in allowed_origins:
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
                st.error({"error": "no_se_pudo_añadir_origen", "detail": upd})
                st.stop()
            st.success("Origen añadido al tenant.")
            st.cache_data.clear()

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
if mode.startswith("Página"):
    st.info("Modo página externa: el widget en vivo no se monta dentro del panel. Usa el token arriba en tu sitio de prueba.")
    st.stop()

def _load_local_widget_assets(widget_src_value: str) -> tuple[str, str] | None:
    """
    Permite usar el build local del repo sin depender de un servidor HTTP.
    Formato: local:frontend-widget/dist/chat-widget.js
    """
    src = (widget_src_value or "").strip()
    if not src.lower().startswith("local:"):
        return None
    rel = src.split(":", 1)[1].strip().lstrip("/")
    js_path = (REPO_ROOT / rel).resolve()
    css_path = js_path.with_name("chatbot-widget.css")
    if not js_path.exists():
        st.error(f"No existe el widget local: `{js_path}`")
        return None
    js = js_path.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
    return js, css


local_assets = _load_local_widget_assets(widget_src)
local_js_b64 = ""
local_css = ""
if local_assets:
    import base64

    local_js_b64 = base64.b64encode(local_assets[0].encode("utf-8")).decode("ascii")
    local_css = local_assets[1] or ""

# Cache-bust: evita servir un JS cacheado por el navegador al cambiar builds (solo HTTP).
widget_src_effective = (widget_src or "").strip()
if widget_src_effective and not widget_src_effective.lower().startswith("local:"):
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
      {local_css}
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
    {"".join([]) if not local_assets else ""}
    <script>
      (function() {{
        const apiBase = {json.dumps(api_base)};
        const token = {json.dumps(token_input)};
        const startOpen = true;
        const tenantId = {json.dumps(str(tenant['id']))};

        const localMode = {json.dumps(bool(local_assets))};
        if (localMode) {{
          const jsB64 = {json.dumps(local_js_b64)};
          const js = atob(jsB64);
          const blob = new Blob([js], {{ type: "text/javascript" }});
          const url = URL.createObjectURL(blob);
          const s = document.createElement("script");
          s.src = url;
          s.async = true;
          s.dataset.api = apiBase;
          s.dataset.apiUrl = apiBase;
          s.dataset.token = token;
          s.dataset.tenant = tenantId;
          s.dataset.startOpen = String(startOpen);
          document.body.appendChild(s);
          return;
        }}

        const src = {json.dumps(widget_src_effective)};
        if (!src) {{
          const err = document.createElement("div");
          err.style.padding = "12px";
          err.style.color = "#b91c1c";
          err.textContent = "Widget JS no configurado. Usa 'local:frontend-widget/dist/chat-widget.js' o pega una URL CDN.";
          document.body.appendChild(err);
          return;
        }}
        const s = document.createElement("script");
        s.src = src;
        s.async = true;
        s.dataset.api = apiBase;
        s.dataset.apiUrl = apiBase;
        s.dataset.token = token;
        s.dataset.tenant = tenantId;
        s.dataset.startOpen = String(startOpen);
        document.body.appendChild(s);
      }})();
    </script>
  </body>
</html>
"""
components.html(html, height=720, scrolling=True)
