import sys
from pathlib import Path

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from admin_panel.api_client import create_tenant
from admin_panel.ui import ensure_vertical_catalog, init_page, render_impersonation_banner, render_sidebar_nav, require_admin_context

init_page(title="SuperAdmin — Crear tenant", icon="➕")

ctx = require_admin_context()
render_sidebar_nav()
render_impersonation_banner()

st.title("Crear tenant")
st.caption("Crea un tenant y provisiona el vertical/scopes.")

vertical_items, vertical_keys, vertical_labels, vertical_by_key = ensure_vertical_catalog(ctx)

col_a, col_b = st.columns(2)
with col_a:
    name = st.text_input("Nombre comercial", key="ct-name")
    contact = st.text_input("Email de contacto", key="ct-email")
    phone = st.text_input("Teléfono de contacto", key="ct-phone")
    plan = st.selectbox("Plan", ["BASE", "PRO", "ELITE"], key="ct-plan")
    vertical_key = st.selectbox(
        "Vertical",
        vertical_keys or ["kitchens"],
        format_func=lambda v: vertical_labels.get(v, v),
        key="ct-vertical",
    )
with col_b:
    st.markdown("**Dirección completa**")
    addr_street = st.text_input("Calle/Av", key="ct-addr-street")
    addr_number = st.text_input("Número", key="ct-addr-number")
    addr_postal = st.text_input("Código postal", key="ct-addr-postal")
    addr_city = st.text_input("Población", key="ct-addr-city")
    origins_new = st.text_input("Allowed origins (coma)", key="ct-origins")
    limit = st.number_input("Límite IA €", min_value=0.0, step=5.0, value=0.0, key="ct-limit")
    maint_new = st.checkbox("Mantenimiento inicial", value=False, key="ct-maint")
    use_ia_new = st.checkbox("IA habilitada", value=True, key="ct-ia")

selected_scopes_new: list[str] = []
selected_vertical = vertical_by_key.get(vertical_key) if vertical_key else None
if isinstance(selected_vertical, dict):
    promise = selected_vertical.get("promise_commercial")
    if promise:
        st.caption(f"Promesa: {promise}")
    files = selected_vertical.get("files") or {}
    if isinstance(files, dict):
        missing = [fname for fname, ok in files.items() if not ok]
        if missing:
            st.warning(f"Vertical incompleto (faltan: {', '.join(missing)})")
    scope_items = selected_vertical.get("scope_items") or []
    scope_labels = {
        str(it.get("key")): (it.get("label") or it.get("key"))
        for it in scope_items
        if isinstance(it, dict) and it.get("key")
    }
    scope_keys = list(scope_labels.keys())
    if scope_keys:
        st.caption("Selecciona 1 o más scopes (sub-verticals) — opciones dependen del vertical.")
        scopes_key = f"ct-scopes-{vertical_key}"
        selected_scopes_new = st.multiselect(
            "Scopes (sub-verticals)",
            scope_keys,
            default=st.session_state.get(scopes_key) or [scope_keys[0]],
            format_func=lambda k: scope_labels.get(k, k),
            key=scopes_key,
        )

if st.button("Crear", use_container_width=True, key="ct-submit"):
    payload = {
        "name": name,
        "contact_email": contact or None,
        "contact_phone": phone or None,
        "address_street": addr_street or None,
        "address_number": addr_number or None,
        "address_postal_code": addr_postal or None,
        "address_city": addr_city or None,
        "plan": plan,
        "ia_monthly_limit_eur": limit,
        "allowed_origins": [o.strip() for o in origins_new.split(",") if o.strip()],
        "maintenance": maint_new,
        "use_ia": use_ia_new,
        "ia_enabled": use_ia_new,
        "vertical_key": vertical_key,
        "vertical_scopes": selected_scopes_new,
    }
    res = create_tenant(ctx.token, payload, api_key=ctx.api_key)
    if res and "id" in res:
        st.success(f"Tenant creado: {res['id']}")
    else:
        st.error(res)
