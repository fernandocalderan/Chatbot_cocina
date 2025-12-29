import sys
from pathlib import Path

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from admin_panel.api_client import create_vertical_admin, get_vertical, read_vertical_file_admin, update_vertical_file_admin
from admin_panel.ui import can_write, ensure_vertical_catalog, init_page, render_impersonation_banner, render_sidebar_nav, require_admin_context

init_page(title="SuperAdmin — Verticals", icon="🧩")

ctx = require_admin_context()
render_sidebar_nav()
render_impersonation_banner()

st.title("Verticals")
st.caption("Catálogo de verticales (plantillas ADMIN) detectadas por la API.")

write_enabled = can_write(ctx) and not st.session_state.get("impersonation_token")
if not write_enabled:
    st.info("Modo solo lectura: edición/creación de verticales está desactivada.")


def _show_api_error(payload: object, fallback: str) -> None:
    if isinstance(payload, dict) and payload.get("error"):
        st.error(f"{fallback} (HTTP {payload.get('status_code', 'N/A')}): {payload.get('error')}")


vertical_items, vertical_keys, vertical_labels, _ = ensure_vertical_catalog(ctx)
if not vertical_items:
    st.warning("No se han encontrado verticales.")
    vertical_items = []
    vertical_keys = []
    vertical_labels = {}

with st.expander("➕ Crear vertical", expanded=False):
    st.caption("Crea un vertical nuevo y su `flow_base.json` inicial (válido).")
    with st.form("create-vertical"):
        ck1, ck2 = st.columns([0.4, 0.6])
        new_key = ck1.text_input("Key (slug)", placeholder="ej: dental_clinics", disabled=not write_enabled)
        new_label = ck2.text_input("Label", placeholder="Nombre comercial", disabled=not write_enabled)
        default_flow_id = st.text_input("Default flow id", placeholder="ej: dental_clinics_base_v1", disabled=not write_enabled)
        flow_file = st.file_uploader("flow_base.json (opcional)", type=["json"], disabled=not write_enabled)
        submitted = st.form_submit_button("Crear", use_container_width=True, disabled=not write_enabled)
    if submitted:
        flow_base = None
        if flow_file is not None:
            try:
                import json as _json

                flow_base = _json.loads(flow_file.getvalue().decode("utf-8"))
            except Exception as exc:
                st.error(f"flow_base.json inválido: {exc}")
                flow_base = None
        payload = {
            "key": (new_key or "").strip(),
            "label": (new_label or "").strip() or None,
            "default_flow_id": (default_flow_id or "").strip() or None,
            "flow_base": flow_base,
        }
        res = create_vertical_admin(ctx.token, payload, api_key=ctx.api_key)
        if isinstance(res, dict) and res.get("error"):
            _show_api_error(res, "No se pudo crear el vertical")
        else:
            st.success("Vertical creado.")
            st.session_state.pop("_admin_vertical_catalog", None)
            st.rerun()

st.markdown("**Detalle de vertical**")
selected_key = st.selectbox(
    "Selecciona un vertical",
    vertical_keys or [],
    format_func=lambda v: vertical_labels.get(v, v),
    key="vertical-detail-select",
)
if selected_key:
    detail = get_vertical(ctx.token, selected_key, api_key=ctx.api_key) or {}
    if detail.get("error"):
        _show_api_error(detail, "No se pudo cargar el vertical")
    else:
        cfg = detail.get("config") if isinstance(detail.get("config"), dict) else {}
        assets = detail.get("assets") if isinstance(detail.get("assets"), dict) else {}
        files = detail.get("files") if isinstance(detail.get("files"), dict) else {}
        st.markdown(f"**Key:** `{detail.get('key') or selected_key}`")
        promise = cfg.get("promise_commercial")
        if promise:
            st.caption(f"Promesa: {promise}")
        missing = [fname for fname, ok in files.items() if not ok] if files else []
        if missing:
            st.warning(f"Vertical incompleto (faltan: {', '.join(missing)})")
        with st.expander("metadata.json", expanded=False):
            st.json(assets.get("metadata") or cfg or {})
        with st.expander("flow_base.json", expanded=False):
            st.json(assets.get("flow_base") or {})
        with st.expander("semantic_schema.json", expanded=False):
            st.json(assets.get("semantic_schema") or {})
        with st.expander("kpi_defaults.json", expanded=False):
            st.json(assets.get("kpi_defaults") or {})
        with st.expander("prompt_vertical.txt", expanded=False):
            st.code(assets.get("prompt_vertical") or "", language="text")
        with st.expander("prompt_vertical_extension.txt", expanded=False):
            st.code(assets.get("prompt_vertical_extension") or "", language="text")

        st.divider()
        st.subheader("Editar assets")
        st.caption("Guarda cambios directamente en `backend/app/verticals/<key>/...` (requiere volumen persistente en prod).")

        def _json_editor(title: str, filename: str, value: dict):
            state_key = f"_v_edit_{selected_key}_{filename}"
            if state_key not in st.session_state:
                import json as _json

                st.session_state[state_key] = _json.dumps(value or {}, ensure_ascii=False, indent=2)
            st.markdown(f"**{title}** (`{filename}`)")
            txt = st.text_area(
                f"{filename} editor",
                value=st.session_state[state_key],
                height=220 if filename != "flow_base.json" else 360,
                key=f"{state_key}_ta",
                disabled=not write_enabled,
            )
            c1, c2 = st.columns([0.6, 0.4])
            upload = c2.file_uploader(f"Subir {filename}", type=["json"], key=f"{state_key}_up", disabled=not write_enabled)
            if upload is not None and write_enabled:
                try:
                    st.session_state[state_key] = upload.getvalue().decode("utf-8")
                    st.success(f"{filename} cargado en el editor.")
                except Exception as exc:
                    st.error(f"No se pudo leer archivo: {exc}")
            if c1.button(f"Guardar {filename}", key=f"{state_key}_save", disabled=not write_enabled):
                try:
                    import json as _json

                    obj = _json.loads(txt or "{}")
                    if not isinstance(obj, dict):
                        raise ValueError("Debe ser un objeto JSON (dict).")
                except Exception as exc:
                    st.error(f"JSON inválido: {exc}")
                    return
                if filename in {"flow_base.json"} or filename.startswith("flow_scope_"):
                    st.caption("Validando flow…")
                out = update_vertical_file_admin(
                    ctx.token,
                    selected_key,
                    filename,
                    kind="json",
                    content=obj,
                    validate=True,
                    api_key=ctx.api_key,
                )
                if isinstance(out, dict) and out.get("error"):
                    _show_api_error(out, f"No se pudo guardar {filename}")
                else:
                    st.success(f"{filename} guardado.")
                    st.session_state.pop("_admin_vertical_catalog", None)
                    st.rerun()

        def _text_editor(title: str, filename: str, value: str):
            state_key = f"_v_edit_{selected_key}_{filename}"
            if state_key not in st.session_state:
                st.session_state[state_key] = (value or "").strip()
            st.markdown(f"**{title}** (`{filename}`)")
            txt = st.text_area(
                f"{filename} editor",
                value=st.session_state[state_key],
                height=200,
                key=f"{state_key}_ta",
                disabled=not write_enabled,
            )
            c1, c2 = st.columns([0.6, 0.4])
            upload = c2.file_uploader(f"Subir {filename}", type=["txt"], key=f"{state_key}_up", disabled=not write_enabled)
            if upload is not None and write_enabled:
                try:
                    st.session_state[state_key] = upload.getvalue().decode("utf-8")
                    st.success(f"{filename} cargado en el editor.")
                except Exception as exc:
                    st.error(f"No se pudo leer archivo: {exc}")
            if c1.button(f"Guardar {filename}", key=f"{state_key}_save", disabled=not write_enabled):
                out = update_vertical_file_admin(
                    ctx.token,
                    selected_key,
                    filename,
                    kind="text",
                    content=txt,
                    validate=False,
                    api_key=ctx.api_key,
                )
                if isinstance(out, dict) and out.get("error"):
                    _show_api_error(out, f"No se pudo guardar {filename}")
                else:
                    st.success(f"{filename} guardado.")
                    st.session_state.pop("_admin_vertical_catalog", None)
                    st.rerun()

        _json_editor("metadata", "metadata.json", assets.get("metadata") if isinstance(assets.get("metadata"), dict) else {})
        _json_editor("flow_base", "flow_base.json", assets.get("flow_base") if isinstance(assets.get("flow_base"), dict) else {})
        _json_editor(
            "semantic_schema",
            "semantic_schema.json",
            assets.get("semantic_schema") if isinstance(assets.get("semantic_schema"), dict) else {},
        )
        _json_editor(
            "kpi_defaults",
            "kpi_defaults.json",
            assets.get("kpi_defaults") if isinstance(assets.get("kpi_defaults"), dict) else {},
        )
        _text_editor("prompt_vertical", "prompt_vertical.txt", assets.get("prompt_vertical") or "")
        _text_editor(
            "prompt_vertical_extension",
            "prompt_vertical_extension.txt",
            assets.get("prompt_vertical_extension") or "",
        )

        st.markdown("**Flows por scope (opcional)**")
        scope_items = cfg.get("scope_definitions") if isinstance(cfg.get("scope_definitions"), dict) else {}
        scope_keys = list(scope_items.keys())
        if scope_keys:
            scope_key = st.selectbox("Scope", options=scope_keys, key="scope-flow-select")
            filename = f"flow_scope_{scope_key}.json"
            existing_scope_flow = {}
            read = read_vertical_file_admin(ctx.token, selected_key, filename, api_key=ctx.api_key)
            if isinstance(read, dict) and isinstance(read.get("content"), dict):
                existing_scope_flow = read.get("content") or {}
            _json_editor(f"flow_scope {scope_key}", filename, existing_scope_flow)
        else:
            st.caption("Este vertical no define `scope_definitions`; no hay flows por scope.")

st.divider()
st.subheader("Lista")
for v in vertical_items:
    key = v.get("key")
    label = v.get("label") or key
    with st.expander(f"{label} — {key}", expanded=False):
        promise = v.get("promise_commercial")
        if promise:
            st.markdown(f"**Promesa comercial:** {promise}")
        st.markdown(f"**Default flow:** `{v.get('default_flow_id') or 'n/d'}`")
        ci = v.get("conversational_intelligence") or {}
        if isinstance(ci, dict) and ci:
            st.markdown("**CI v1.1:**")
            st.json(ci)
        scope = v.get("scope") or {}
        if isinstance(scope, dict) and scope:
            st.markdown("**Scope:**")
            st.json(scope)
        files = v.get("files") or {}
        if isinstance(files, dict) and files:
            missing = [fname for fname, ok in files.items() if not ok]
            if missing:
                st.warning(f"Faltan archivos: {', '.join(missing)}")
            else:
                st.success("Archivos mínimos OK.")
        if v.get("flow_template_exists") is False:
            st.warning("No hay flujo disponible (falta `flow_base.json` y no hay fallback en `backend/app/flows/`).")
        else:
            st.caption(f"Fuente de flujo en runtime: `{v.get('flow_source') or 'n/d'}`")
