import sys
from pathlib import Path

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from admin_panel.api_client import create_scope, get_catalog, flatten_catalog_scopes
from admin_panel.ui import init_page, render_sidebar_nav, require_admin_context, pill
from admin_panel.panel_utils import open_wizard

init_page(title="SuperAdmin — Scopes", icon="🧭")

ctx = require_admin_context()
render_sidebar_nav()

st.title("Scopes")
st.caption("Catálogo único (FS + DB). Incluye scopes vacíos.")
st.info("Modo lectura. Usa el Wizard para crear/editar scopes (activar Debug para acciones avanzadas).")

debug_mode = bool(st.session_state.get("debug"))

col1, col2, col3 = st.columns([0.4, 0.3, 0.3])
include_empty = col1.toggle("Incluir vacíos", value=True)
include_drafts = col2.toggle("Incluir drafts", value=True)
include_templates = col3.toggle("Incluir templates FS", value=True)

with st.spinner("Cargando catálogo…"):
    catalog = get_catalog(
        ctx.token,
        include_empty_scopes=include_empty,
        include_drafts=include_drafts,
        include_templates=include_templates,
        api_key=ctx.api_key,
    )

if isinstance(catalog, dict) and catalog.get("error"):
    st.error(catalog)
    st.stop()

rows = flatten_catalog_scopes(catalog or {})
verticals = sorted({r["vertical_key"] for r in rows if r.get("vertical_key")})
vertical_sel = st.selectbox("Vertical", options=["Todos"] + verticals, index=0)
if vertical_sel != "Todos":
    rows = [r for r in rows if r.get("vertical_key") == vertical_sel]

st.markdown("**Scopes**")
if debug_mode:
    with st.expander("Crear scope (Debug)", expanded=False):
        c1, c2 = st.columns([0.5, 0.5])
        vertical_input = c1.selectbox(
            "Vertical existente",
            options=verticals or [],
            index=0 if verticals else None,
        )
        vertical_custom = c2.text_input("Vertical (nuevo)", value="")
        scope_key = st.text_input("Scope key", value="", placeholder="ej: osteopatia")
        display_name = st.text_input("Nombre visible", value="", placeholder="Osteopatía")
        description = st.text_area("Descripción (opcional)", value="", height=80)
        vertical_final = (vertical_custom.strip() or vertical_input or "").strip()
        if st.button("Crear scope", use_container_width=True):
            if not vertical_final or not scope_key.strip() or not display_name.strip():
                st.warning("Completa vertical, scope key y nombre visible.")
            else:
                res = create_scope(
                    ctx.token,
                    vertical_key=vertical_final,
                    scope_key=scope_key.strip(),
                    display_name=display_name.strip(),
                    description=description.strip() or None,
                    api_key=ctx.api_key,
                )
                if isinstance(res, dict) and res.get("error"):
                    st.error(res)
                else:
                    st.success("Scope creado.")
                    st.rerun()
else:
    st.caption("Acciones de creación habilitadas solo en Debug.")
if not rows:
    st.info("Sin scopes para los filtros actuales.")
else:
    c1, c2, c3, c4, c5, c6 = st.columns([0.22, 0.2, 0.14, 0.14, 0.14, 0.16])
    c1.caption("Scope")
    c2.caption("Estado")
    c3.caption("Flows")
    c4.caption("Publicado")
    c5.caption("Fuente")
    c6.caption("Acción")
    for row in sorted(rows, key=lambda r: (str(r.get("vertical_key") or ""), str(r.get("scope_key") or ""))):
        status = row.get("status") or "NO_FLOW_YET"
        tone = "info"
        if status == "PUBLISHED_OK":
            tone = "success"
        elif status == "DRAFT_ONLY":
            tone = "warning"
        elif status == "MULTIPLE_PUBLISHED":
            tone = "danger"
        badge = pill(status, tone)
        cc1, cc2, cc3, cc4, cc5, cc6 = st.columns([0.22, 0.2, 0.14, 0.14, 0.14, 0.16])
        cc1.markdown(f"**{row.get('scope_key')}**")
        cc1.caption(row.get("vertical_key"))
        cc2.markdown(badge, unsafe_allow_html=True)
        cc3.write(str(row.get("flows_count") or 0))
        cc4.write(str(row.get("published_count") or 0))
        cc5.write(str(row.get("source") or "FILESYSTEM"))
        action_label = "Ver / Editar"
        if status == "NO_FLOW_YET":
            action_label = "Subir flow base"
        elif status == "DRAFT_ONLY":
            action_label = "Publicar"
        if cc6.button(
            "Abrir en Wizard",
            key=f"scope-action-{row.get('vertical_key')}-{row.get('scope_key')}",
            use_container_width=True,
        ):
            open_wizard(vertical_key=row.get("vertical_key"), scope_key=row.get("scope_key"), step=3)
        if debug_mode and not row.get("has_fs_def"):
            cc2.caption("warning: sin definición FS")
