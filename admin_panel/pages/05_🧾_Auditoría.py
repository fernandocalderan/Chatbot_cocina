import sys
from pathlib import Path

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from admin_panel.api_client import admin_alerts, admin_audits_recent, admin_recent_errors
from admin_panel.ui import init_page, render_impersonation_banner, render_sidebar_nav, require_admin_context

init_page(title="SuperAdmin — Auditoría", icon="🧾")

ctx = require_admin_context()
render_sidebar_nav()
render_impersonation_banner()

st.title("Auditoría")
st.caption("Acciones administrativas y señales del sistema.")


def _show_api_error(payload: object, fallback: str) -> None:
    if isinstance(payload, dict) and payload.get("error"):
        st.error(f"{fallback} (HTTP {payload.get('status_code', 'N/A')}): {payload.get('error')}")


st.subheader("Errores recientes")
err_payload = admin_recent_errors(ctx.token, api_key=ctx.api_key) or {}
_show_api_error(err_payload, "No se pudieron cargar errores recientes")
errs = err_payload.get("items") or []
if not errs:
    st.info("Sin errores recientes")
else:
    for err in errs[:30]:
        st.markdown(f"- {err.get('timestamp', '')} — {err.get('level', '')}: {err.get('message')}")

st.divider()
st.subheader("Alertas activas")
alert_payload = admin_alerts(ctx.token, api_key=ctx.api_key) or {}
_show_api_error(alert_payload, "No se pudieron cargar alertas")
alerts = alert_payload.get("items") or []
if not alerts:
    st.info("Sin alertas")
else:
    for a in alerts:
        sev = a.get("severity", "info")
        icon = "🟢"
        if sev == "warning":
            icon = "🟠"
        elif sev == "critical":
            icon = "🔴"
        st.markdown(f"- {icon} {a.get('tenant')}: {a.get('message')}")

st.divider()
st.subheader("Acciones admin (audits)")

f1, f2, f3, f4 = st.columns([0.35, 0.25, 0.25, 0.15])
tenant_filter = f1.text_input("Filtrar por tenant_id", value="", placeholder="UUID")
action_prefix = f2.text_input("Action prefix", value="", placeholder="tenant.")
actor_filter = f3.text_input("Actor contiene", value="", placeholder="email / admin_api_key")
limit = int(f4.number_input("Límite", min_value=10, max_value=200, value=50, step=10))

with st.spinner("Cargando auditoría…"):
    audits = admin_audits_recent(
        ctx.token,
        api_key=ctx.api_key,
        tenant_id=tenant_filter.strip() or None,
        action_prefix=action_prefix.strip() or None,
        actor=actor_filter.strip() or None,
        limit=limit,
    )
    _show_api_error(audits, "No se pudo cargar la auditoría")
    items = audits.get("items") if isinstance(audits, dict) else []

if not items:
    st.info("Sin registros.")
else:
    # Streamlit formatea mejor si son dicts planos.
    rows = []
    for it in items:
        rows.append(
            {
                "created_at": it.get("created_at"),
                "tenant_id": it.get("tenant_id"),
                "action": it.get("action"),
                "entity": it.get("entity"),
                "entity_id": it.get("entity_id"),
                "actor": it.get("actor"),
                "metadata": it.get("metadata"),
            }
        )
    st.dataframe(rows, use_container_width=True, hide_index=True)
