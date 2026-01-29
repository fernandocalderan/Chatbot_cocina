import sys
from pathlib import Path

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from admin_panel.api_client import get_catalog, flatten_catalog_scopes
from admin_panel.ui import init_page, render_sidebar_nav, require_admin_context, pill

init_page(title="SuperAdmin — Scopes", icon="🧭")

ctx = require_admin_context()
render_sidebar_nav()

st.title("Scopes")
st.caption("Catálogo único (FS + DB). Incluye scopes vacíos.")

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
        cc6.button(
            action_label,
            key=f"scope-action-{row.get('vertical_key')}-{row.get('scope_key')}",
            disabled=True,
            help="Acción disponible en Fase 2.",
            use_container_width=True,
        )
        if debug_mode and not row.get("has_fs_def"):
            cc2.caption("warning: sin definición FS")
