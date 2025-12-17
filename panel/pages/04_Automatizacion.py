import json

import streamlit as st

from auth import ensure_login
from nav import render_sidebar, legacy_redirect_with_tab, nav_v2_enabled
from api_client import fetch_flow, update_flow, get_quota_status, get_ia_metrics, get_tenant_kpis, get_tenant_config
from utils import load_styles, empty_state, metric_card, render_quota_banner, render_quota_usage_bar

st.set_page_config(page_title="Automatización", page_icon="🤖", layout="wide")
load_styles()
ensure_login()
if nav_v2_enabled():
    legacy_redirect_with_tab("/Automatizacion", "pages/automatizacion.py", "flujo")
    st.stop()
render_sidebar()

st.title("Automatización")
st.caption("Ajusta cómo responde el asistente y el nivel de automatización.")

tab_flow, tab_brand, tab_level = st.tabs(
    ["Cómo responde el asistente", "Imagen y mensajes", "Nivel de automatización"]
)

with tab_flow:
    st.subheader("Cómo responde el asistente")
    st.caption("Edita mensajes y opciones sin tocar cosas técnicas.")

    show_advanced = st.toggle(
        "Modo avanzado",
        value=False,
        help="Muestra identificadores y estructura técnica del flujo.",
    )

    flow_key = "_flow_data"
    if st.button("Cargar flujo", use_container_width=True):
        with st.spinner("Cargando…"):
            flow = fetch_flow()
        if isinstance(flow, dict) and isinstance(flow.get("flow"), dict):
            st.session_state[flow_key] = flow["flow"]
        else:
            empty_state("No pudimos cargar el flujo", "Estamos cargando la información. El asistente sigue activo.", icon="⚠️")

    flow_data = st.session_state.get(flow_key)
    if not flow_data:
        empty_state("Sin cambios por hacer ahora", "Carga el flujo para revisar y ajustar los mensajes.", icon="✨")
    else:
        blocks = flow_data.get("blocks", {}) or {}
        block_items = list(blocks.items())

        st.markdown("### Mensajes")
        if not block_items:
            empty_state("No hay bloques", "Este flujo no tiene bloques para editar.", icon="🧩")
        else:
            editing_key = "_editing_block"
            for idx, (block_id, block) in enumerate(block_items, start=1):
                text = block.get("text") or {}
                es = (text.get("es") if isinstance(text, dict) else "") or ""
                title = f"Mensaje {idx}"
                if show_advanced:
                    title = f"{title} · {block_id}"
                snippet = (es or "").strip().split("\n")[0][:80]
                with st.expander(f"{title}{(' — ' + snippet) if snippet else ''}", expanded=False):
                    col_a, col_b = st.columns(2)
                    text_es = col_a.text_area("Texto (ES)", value=(text.get("es") if isinstance(text, dict) else "") or "", key=f"es-{block_id}")
                    text_en = col_b.text_area("Texto (EN)", value=(text.get("en") if isinstance(text, dict) else "") or "", key=f"en-{block_id}")
                    text_pt = col_a.text_area("Texto (PT)", value=(text.get("pt") if isinstance(text, dict) else "") or "", key=f"pt-{block_id}")
                    text_ca = col_b.text_area("Texto (CA)", value=(text.get("ca") if isinstance(text, dict) else "") or "", key=f"ca-{block_id}")

                    if st.button("Guardar", key=f"save-{block_id}", use_container_width=True):
                        if not isinstance(block.get("text"), dict):
                            block["text"] = {}
                        block["text"] = {"es": text_es, "en": text_en, "pt": text_pt, "ca": text_ca}
                        flow_data["blocks"][block_id] = block
                        with st.spinner("Guardando…"):
                            res = update_flow(flow_data)
                        if isinstance(res, dict) and res.get("status_code"):
                            empty_state("No pudimos guardar ahora", "Estamos cargando la información. El asistente sigue activo.", icon="⚠️")
                        else:
                            st.success("Guardado.")

        if show_advanced:
            with st.expander("Ver JSON (avanzado)", expanded=False):
                st.code(json.dumps(flow_data, ensure_ascii=False, indent=2), language="json")

with tab_brand:
    st.subheader("Imagen y mensajes")
    st.caption("Lo que ve tu cliente: nombre, logo y tono.")

    cfg = get_tenant_config() or {}
    if isinstance(cfg, dict) and cfg.get("status_code"):
        empty_state("No pudimos cargar la configuración", "Estamos cargando la información. El asistente sigue activo.", icon="⚠️")
    else:
        name = st.session_state.get("tenant_name") or cfg.get("name") or "Tu negocio"
        logo = st.session_state.get("tenant_logo_url") or cfg.get("logo_url")
        lang = st.session_state.get("tenant_language") or cfg.get("language") or "es"
        tz = st.session_state.get("tenant_timezone") or cfg.get("timezone") or "Europe/Madrid"

        c1, c2 = st.columns([0.6, 0.4])
        with c1:
            st.markdown("### Identidad")
            st.text_input("Nombre comercial", value=str(name), disabled=True)
            st.text_input("Idioma", value=str(lang).upper(), disabled=True)
            st.text_input("Zona horaria", value=str(tz), disabled=True)
        with c2:
            st.markdown("### Logo")
            if logo:
                st.image(logo, width=170)
            else:
                empty_state("Sin logo", "Puedes añadirlo en Configuración → Widget.", icon="🖼️")

        st.markdown("### Mensajes")
        st.caption("Los mensajes se ajustan en “Cómo responde el asistente”.")

with tab_level:
    st.subheader("Nivel de automatización")
    st.caption("Estado de la IA, consumo del mes y avisos de límite.")

    tenant_id = st.session_state.get("tenant_id")
    quota = get_quota_status() or {}
    quota_status = quota.get("quota_status") if isinstance(quota, dict) else {}
    if not isinstance(quota_status, dict):
        quota_status = {}

    kpis = get_tenant_kpis() or {}
    kpi_data = kpis.get("kpis") if isinstance(kpis, dict) and isinstance(kpis.get("kpis"), dict) else {}
    ia_metrics = get_ia_metrics(tenant_id) if tenant_id else {}
    monthly = ia_metrics.get("monthly") if isinstance(ia_metrics, dict) and isinstance(ia_metrics.get("monthly"), dict) else {}

    spent = float((monthly.get("total_cost_eur") if isinstance(monthly, dict) else 0.0) or 0.0)
    limit = float((quota_status.get("limit_eur") if isinstance(quota_status, dict) else 0.0) or (kpi_data.get("ai_limit_eur") or 0.0) or 0.0)
    mode = str((quota_status.get("mode") if isinstance(quota_status, dict) else "") or "ACTIVE").upper()

    needs_upgrade = bool(quota_status.get("needs_upgrade_notice")) if isinstance(quota_status, dict) else False
    render_quota_banner(quota_status, needs_upgrade=needs_upgrade)
    render_quota_usage_bar(quota_status, label="Consumo IA mensual")

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Estado IA", "IA activa" if mode == "ACTIVE" else ("Modo ahorro" if mode == "SAVING" else "Bloqueado"), subtitle="", accent="#0D9488" if mode == "ACTIVE" else "#B45309")
    with c2:
        metric_card("Consumo (mes)", f"{spent:.2f} €", subtitle="A la fecha", accent="#1E88E5")
    with c3:
        metric_card("Límite (mes)", f"{limit:.2f} €" if limit else "—", subtitle="Tu plan", accent="#111827")

    if mode != "ACTIVE":
        empty_state("El asistente sigue activo", "Podrás seguir captando oportunidades, pero algunas respuestas pueden simplificarse.", icon="✨")
