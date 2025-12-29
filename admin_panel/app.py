import sys
from pathlib import Path

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from admin_panel.ui import init_page, render_impersonation_banner, render_sidebar_nav, require_admin_context

init_page(title="Opunnence SuperAdmin", icon="🛠️")

st.title("Opunnence — SuperAdmin")
st.caption("Panel de administración global (tenants, verticales, tokens, flows).")

ctx = require_admin_context()
render_sidebar_nav()
render_impersonation_banner()

with st.sidebar:
    role_label = ", ".join(ctx.roles) if ctx.roles else "N/D"
    st.caption(f"Rol: `{role_label}`")

st.markdown(
    """
**Atajos**
- `Overview`: salud del sistema, alertas, errores y costes.
- `Tenants`: edición, tokens, flows e impersonación.
- `Auditoría`: acciones admin recientes.
"""
)

col1, col2 = st.columns(2)
with col1:
    st.page_link("pages/01_📊_Overview.py", label="Abrir Overview", icon="📊")
    st.page_link("pages/02_🏢_Tenants.py", label="Abrir Tenants", icon="🏢")
with col2:
    st.page_link("pages/05_🧾_Auditoría.py", label="Abrir Auditoría", icon="🧾")
    st.page_link("pages/widget_tester.py", label="Abrir Widget tester", icon="🧪")
