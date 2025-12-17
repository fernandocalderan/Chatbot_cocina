from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from auth import ensure_login
from nav import legacy_redirect, nav_v2_enabled, render_sidebar, show_flash
from utils import load_styles, empty_state, loading_state, pill
from api_client import (
    get_lead,
    chat_history,
    list_appointments,
    confirm_appointment,
    cancel_appointment,
    reschedule_appointment,
    download_lead_pdf,
    update_lead_panel,
)
from crm_ui import (
    human_status,
    priority_label,
    lead_person,
    recommended_action,
    safe_chat_html,
    human_project_type,
    human_urgency,
    quote_status_human,
    format_day,
    format_time,
    day_bucket,
)

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None

st.set_page_config(page_title="Relatório", page_icon="🧾", layout="wide")
load_styles()
ensure_login()
render_sidebar()
show_flash()

lead_id = None
try:
    lead_id = st.query_params.get("lead_id")
    if isinstance(lead_id, list):
        lead_id = lead_id[0] if lead_id else None
    lead_id = str(lead_id) if lead_id else None
except Exception:
    lead_id = None

if nav_v2_enabled():
    # Ruta legacy: Relatório ya no existe como pantalla independiente en V2.
    # Compatibilidad:
    # - /Relatorio?lead_id=XYZ -> /oportunidades (con lead seleccionado)
    # - /Relatorio (sin contexto) -> /oportunidades (mensaje humano)
    if lead_id:
        st.session_state["selected_lead_id"] = lead_id
        legacy_redirect("/Relatorio", "pages/oportunidades.py")
    else:
        st.session_state.pop("selected_lead_id", None)
        legacy_redirect("/Relatorio", "pages/oportunidades.py", flash_message="Selecciona una oportunidad para continuar.")
    st.stop()

# Modo legacy (V1): mantener el detalle operativo sin nested expanders.
tenant_tz = st.session_state.get("tenant_timezone", "Europe/Madrid")
tenant_currency = str(st.session_state.get("tenant_currency") or "EUR").upper()

lead_id = lead_id or st.session_state.get("selected_lead_id")
if not lead_id:
    empty_state("Selecciona una oportunidad", "Abre Oportunidades y toca “Ver detalles”.", icon="🧾")
    if st.button("Ir a Oportunidades", use_container_width=True):
        st.switch_page("pages/02_Oportunidades.py")
    st.stop()

loader = st.empty()
with loader.container():
    loading_state()
lead = get_lead(str(lead_id)) or {}
loader.empty()
if isinstance(lead, dict) and lead.get("status_code"):
    empty_state("No pudimos cargar este lead", "Estamos cargando la información. El asistente sigue activo.", icon="⚠️")
    if st.button("Volver", use_container_width=True):
        st.switch_page("pages/02_Oportunidades.py")
    st.stop()

person = lead_person(lead)
status_h = human_status(lead.get("status"))
prio = priority_label(lead)

st.markdown("## Relatório")

# Header del Lead
left, right = st.columns([0.65, 0.35])
with left:
    st.subheader(person.display_name)
    line = []
    if person.phone:
        line.append(f"[📞 {person.phone}](tel:{person.phone})")
    if person.email:
        line.append(f"[📧 {person.email}](mailto:{person.email})")
    if line:
        st.markdown(" · ".join(line))
    st.markdown(
        f"{pill(status_h, tone='info')} {pill(prio, tone='danger' if prio.startswith('🔥') else ('warning' if prio.startswith('⚡') else 'info'))}",
        unsafe_allow_html=True,
    )
with right:
    a = st.columns(3)
    if person.phone:
        a[0].link_button("📞 Llamar", url=f"tel:{person.phone}", use_container_width=True)
    if person.email:
        a[1].link_button("📧 Email", url=f"mailto:{person.email}", use_container_width=True)
    a[2].page_link("pages/03_Agenda.py", label="📅 Cita", use_container_width=True)

vars_ = lead.get("variables") if isinstance(lead.get("variables"), dict) else {}
meta = lead.get("metadata") if isinstance(lead.get("metadata"), dict) else {}
appts = list_appointments(lead_id=str(lead_id), limit=50) or []

quote_status = quote_status_human(meta.get("quote_status"))
has_appt = any(a.get("status") in {"booked", "confirmed"} for a in appts)
next_step = recommended_action(lead.get("status"), has_appointment=has_appt)
st.markdown(f"**Acción recomendada:** {next_step}")

# Resumen (colapsable)
with st.expander("Resumen del cliente", expanded=True):
    st.caption("Entiende el lead en 10 segundos.")
    project_type = human_project_type(vars_.get("project_type") or vars_.get("tipo_proyecto"))
    budget = vars_.get("budget") or vars_.get("presupuesto")
    urgency = human_urgency(vars_.get("urgency") or vars_.get("urgencia"))
    style = vars_.get("style") or vars_.get("estilo")
    sqm = vars_.get("sqm") or vars_.get("metros_cuadrados") or vars_.get("m2")
    objective = vars_.get("objective") or vars_.get("objetivo")

    summary_items = []
    if project_type:
        summary_items.append(("Tipo de proyecto", project_type))
    if budget:
        budget_str = str(budget).strip()
        if budget_str.isdigit():
            budget_str = f"{int(budget_str):,}".replace(",", ".")
        if tenant_currency == "EUR" and budget_str:
            budget_str = f"{budget_str} €"
        summary_items.append(("Presupuesto estimado", budget_str))
    if urgency:
        summary_items.append(("Urgencia", urgency))
    if style:
        summary_items.append(("Estilo", str(style)))
    if sqm:
        sqm_str = str(sqm).strip()
        summary_items.append(("Metros cuadrados", f"{sqm_str} m²" if sqm_str else ""))
    if objective:
        summary_items.append(("Objetivo", str(objective)))

    if not summary_items:
        empty_state("Aún faltan datos del proyecto", "El asistente los irá captando.", icon="✨")
    else:
        cols = st.columns(3)
        for idx, (label, value) in enumerate(summary_items):
            if not value:
                continue
            with cols[idx % 3]:
                st.markdown(f"**{label}**")
                st.write(value)

# Conversación (colapsable)
with st.expander("Conversación con el chatbot", expanded=True):
    sess_id = lead.get("session_id")
    if not sess_id:
        st.caption("No hay conversación asociada a este lead.")
    else:
        history = chat_history(str(sess_id)) or []
        if not history:
            st.caption("Aún no hay mensajes registrados.")
        else:
            for msg in history:
                role = (msg.get("role") or "").lower()
                content = safe_chat_html(str(msg.get("content") or ""))
                if not content:
                    continue
                if role == "user":
                    st.markdown(f'<div class="chat-bubble bubble-user">{content}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-bubble bubble-bot">{content}</div>', unsafe_allow_html=True)

# Presupuesto (colapsable)
with st.expander("Presupuesto", expanded=True):
    st.caption(f"Estado: {quote_status}")
    pcols = st.columns(3)
    pdf_key = f"_pdf_cache_{lead_id}"
    if pcols[0].button("Descargar", use_container_width=True):
        pdf = download_lead_pdf(str(lead_id), kind="comercial") or {}
        if isinstance(pdf, dict) and pdf.get("content"):
            st.session_state[pdf_key] = pdf
            st.rerun()

    cached_pdf = st.session_state.get(pdf_key)
    if isinstance(cached_pdf, dict) and cached_pdf.get("content"):
        st.download_button(
            "Descargar",
            data=cached_pdf["content"],
            file_name="presupuesto.pdf",
            mime=cached_pdf.get("content_type") or "application/pdf",
            use_container_width=True,
        )

    if pcols[1].button("Reenviar", use_container_width=True):
        update_lead_panel(str(lead_id), quote_status="sent")
        st.success("Marcado como enviado.")

    if pcols[2].button("Enviado", use_container_width=True):
        update_lead_panel(str(lead_id), quote_status="sent")
        st.success("Marcado como enviado.")

# Citas (sin nested expanders)
st.subheader("Citas")
if not appts:
    st.caption("Aún no hay citas para este lead.")
else:
    tz_obj = ZoneInfo(tenant_tz) if ZoneInfo else timezone.utc
    today = datetime.now(tz=tz_obj).date()
    for appt in sorted(appts, key=lambda a: a.get("slot_start") or ""):
        appt_id = appt.get("id")
        start = appt.get("slot_start")
        status = appt.get("status") or ""
        appt_date = format_day(start, tz_name=tenant_tz)
        bucket = day_bucket(appt_date, today) if appt_date else ""
        hour = format_time(start, tz_name=tenant_tz)
        when = f"{bucket} {hour}".strip()
        header = f"{when} · {human_status(status)}".strip(" ·")
        with st.expander(header, expanded=False):
            visit_type = (appt.get("visit_type") or "").lower()
            tipo = "Llamada" if visit_type in {"chat", "call", "llamada"} else ("Visita" if visit_type else "")
            st.markdown(
                f"{pill(tipo or 'Cita', tone='info')} {pill(human_status(status), tone='success' if status=='confirmed' else 'warning')}",
                unsafe_allow_html=True,
            )
            b = st.columns(3)
            if appt_id and status != "confirmed" and b[0].button("Confirmar", key=f"confirm-{appt_id}", use_container_width=True):
                confirm_appointment(str(appt_id))
                st.success("Cita confirmada.")
                st.rerun()
            if appt_id and b[1].button("Cancelar", key=f"cancel-{appt_id}", use_container_width=True):
                cancel_appointment(str(appt_id))
                st.success("Cita cancelada.")
                st.rerun()
            if appt_id:
                date_in = st.date_input("Nueva fecha", key=f"d-{appt_id}")
                time_in = st.time_input("Nueva hora", key=f"t-{appt_id}")
                if b[2].button("Reprogramar", key=f"resched-{appt_id}", use_container_width=True):
                    tz = ZoneInfo(tenant_tz) if ZoneInfo else timezone.utc
                    slot_local = datetime.combine(date_in, time_in).replace(tzinfo=tz)
                    slot_iso = slot_local.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
                    reschedule_appointment(str(appt_id), slot_iso)
                    st.success("Cita reprogramada.")
                    st.rerun()

# Notas internas (colapsable)
with st.expander("Notas internas", expanded=True):
    note_key = f"note_{lead_id}"
    default_note = str(meta.get("internal_note") or "")
    if note_key not in st.session_state:
        st.session_state[note_key] = default_note
    st.text_area("Solo visible para tu negocio.", key=note_key, height=110, label_visibility="visible")
    ncols = st.columns([0.22, 0.78])
    if ncols[0].button("Guardar", use_container_width=True):
        update_lead_panel(str(lead_id), internal_note=st.session_state.get(note_key, ""))
        st.success("Nota guardada.")
    ncols[1].caption("Ejemplos: “Llamar después de las 18h”, “Comparar con presupuesto anterior”.")

st.stop()
