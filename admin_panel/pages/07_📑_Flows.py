import sys
from pathlib import Path

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from admin_panel.api_client import get_catalog, flatten_catalog_flows
from admin_panel.ui import init_page, render_sidebar_nav, require_admin_context, pill
from admin_panel.panel_utils import open_verticals

init_page(title="SuperAdmin — Flows", icon="📑")

ctx = require_admin_context()
render_sidebar_nav()

st.title("Flows")
st.caption("Listado global desde /v1/catalog (sin filtros ocultos).")
st.info("Modo lectura. Gestiona flows en Verticals.")
if st.button("Gestionar en Verticals", use_container_width=True):
    open_verticals(tab="Flow base")

col1, col2, col3, col4 = st.columns([0.25, 0.25, 0.25, 0.25])
include_empty = col1.toggle("Incluir vacíos", value=True)
include_drafts = col2.toggle("Incluir drafts", value=True)
include_templates = col3.toggle("Incluir templates FS", value=True)
only_published = col4.toggle("Solo publicados", value=False)

with st.spinner("Cargando catálogo…"):
    catalog = get_catalog(
        ctx.token,
        include_empty_scopes=include_empty,
        include_drafts=include_drafts,
        include_templates=include_templates,
        only_published=only_published,
        api_key=ctx.api_key,
    )

if isinstance(catalog, dict) and catalog.get("error"):
    st.error(catalog)
    st.stop()

rows = flatten_catalog_flows(catalog or {})
verticals = sorted({r["vertical_key"] for r in rows if r.get("vertical_key")})
v_sel = st.selectbox("Vertical", options=["Todos"] + verticals, index=0)
if v_sel != "Todos":
    rows = [r for r in rows if r.get("vertical_key") == v_sel]
scopes = sorted({r["scope_key"] for r in rows if r.get("scope_key")})
s_sel = st.selectbox("Scope", options=["Todos"] + scopes, index=0)
if s_sel != "Todos":
    rows = [r for r in rows if r.get("scope_key") == s_sel]
if only_published:
    rows = [r for r in rows if r.get("published")]

st.markdown("**Flows**")
if not rows:
    st.info("Sin flows para los filtros actuales.")
else:
    c1, c2, c3, c4, c5, c6, c7 = st.columns([0.22, 0.16, 0.14, 0.12, 0.12, 0.12, 0.12])
    c1.caption("Nombre")
    c2.caption("Vertical/Scope")
    c3.caption("Estado")
    c4.caption("Versión")
    c5.caption("Publicado")
    c6.caption("Owner")
    c7.caption("Acción")
    for row in sorted(rows, key=lambda r: (str(r.get("vertical_key") or ""), str(r.get("scope_key") or ""))):
        published = bool(row.get("published"))
        badge = pill("PUBLICADO" if published else "BORRADOR", "success" if published else "warning")
        cc1, cc2, cc3, cc4, cc5, cc6, cc7 = st.columns([0.22, 0.16, 0.14, 0.12, 0.12, 0.12, 0.12])
        cc1.markdown(f"**{row.get('name') or row.get('flow_id')}**")
        cc2.caption(f"{row.get('vertical_key')} · {row.get('scope_key')}")
        cc3.markdown(badge, unsafe_allow_html=True)
        cc4.write(str(row.get("version") or "—"))
        cc5.write(str(row.get("published_at") or "—"))
        cc6.write(str(row.get("owner_type") or "—"))
        action_label = "Gestionar en Verticals"
        action_key = f"flow-action-{row.get('flow_id')}"
        if cc7.button(
            action_label,
            key=action_key,
            use_container_width=True,
        ):
            open_verticals(
                vertical_key=row.get("vertical_key"),
                scope_key=row.get("scope_key"),
                tab="Flow base",
            )
