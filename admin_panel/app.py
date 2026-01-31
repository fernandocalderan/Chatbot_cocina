from __future__ import annotations

import os

import streamlit as st

from admin_panel.ui import init_page, require_admin_context, render_sidebar_nav


def main() -> None:
    init_page(title="SuperAdmin", icon="🛡️")
    st.session_state["_admin_entrypoint"] = "app.py"
    ctx = require_admin_context()
    debug_default = str(os.getenv("PANEL_DEBUG") or "").strip().lower() in {"1", "true", "yes", "on"}
    st.session_state.setdefault("debug", debug_default)
    render_sidebar_nav(show_tools=True)

    st.title("SuperAdmin")
    st.caption("Panel de administración de la plataforma (tenants, flows, auditoría).")

    if not ctx.is_super_admin:
        st.warning("Acceso limitado: no tienes rol SUPER_ADMIN.")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.page_link("pages/01_📊_Overview.py", label="Overview", icon="📊")
    with c2:
        st.page_link("pages/02_🏢_Tenants.py", label="Tenants", icon="🏢")
    with c3:
        st.page_link("pages/03_🧩_Verticals.py", label="Panel de Flows", icon="🧩")


if __name__ == "__main__":
    main()
