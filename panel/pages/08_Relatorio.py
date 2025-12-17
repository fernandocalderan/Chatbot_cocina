from datetime import datetime, timezone, date

import streamlit as st

from auth import ensure_login
from utils import load_styles, pill
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


def _get_query_lead_id() -> str | None:
    try:
        lead_id = st.query_params.get("lead_id")
        if isinstance(lead_id, list):
            lead_id = lead_id[0] if lead_id else None
        return str(lead_id) if lead_id else None
    except Exception:
        return None


def _set_lead_id(lead_id: str | None):
    try:
        if not lead_id:
            if hasattr(st.query_params, "clear"):
                st.query_params.clear()
            else:
                st.query_params["lead_id"] = ""
            return
        st.query_params["lead_id"] = str(lead_id)
    except Exception:
        pass


def _back_to_opps():
    st.session_state.pop("selected_lead_id", None)
    _set_lead_id(None)
    try:
        st.switch_page("pages/02_Oportunidades.py")
    except Exception:
        pass
    st.stop()


tenant_tz = st.session_state.get("tenant_timezone", "Europe/Madrid")
tenant_currency = str(st.session_state.get("tenant_currency") or "EUR").upper()

lead_id = _get_query_lead_id() or st.session_state.get("selected_lead_id")
if not lead_id:
    st.info("Selecciona un lead desde Oportunidades.")
    if st.button("Ir a Oportunidades", use_container_width=True):
        _back_to_opps()
    st.stop()

lead = get_lead(str(lead_id)) or {}
if isinstance(lead, dict) and lead.get("status_code"):
    st.info("No pudimos cargar este lead ahora mismo.")
    if st.button("Volver", use_container_width=True):
        _back_to_opps()
    st.stop()

person = lead_person(lead)
status_h = human_status(lead.get("status"))
prio = priority_label(lead)

top = st.columns([0.18, 0.82])
if top[0].button("← Volver", use_container_width=True):
    _back_to_opps()
top[1].markdown("## Relatório")

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
    st.caption(f"{status_h} · {prio}")
with right:
    a = st.columns(3)
    if person.phone:
        a[0].link_button("📞 Llamar", url=f"tel:{person.phone}", use_container_width=True)
    if person.email:
        a[1].link_button("📧 Email", url=f"mailto:{person.email}", use_container_width=True)
    a[2].page_link("pages/03_Agenda.py", label="📅 Ver / crear cita", use_container_width=True)

vars_ = lead.get("variables") if isinstance(lead.get("variables"), dict) else {}
meta = lead.get("metadata") if isinstance(lead.get("metadata"), dict) else {}
appts = list_appointments(lead_id=str(lead_id), limit=50) or []

# Paso y siguiente acción
quote_status = quote_status_human(meta.get("quote_status"))
has_appt = any(a.get("status") in {"booked", "confirmed"} for a in appts)
next_step = recommended_action(lead.get("status"), has_appointment=has_appt)
steps = ["Lead", "Relatório", "Presupuesto", "Cita", "Cierre"]
done = {"Lead", "Relatório"}
if quote_status in {"Generado", "Enviado"}:
    done.add("Presupuesto")
if has_appt:
    done.add("Cita")
if status_h in {"Perdido"}:
    done.add("Cierre")
st.markdown(
    " ".join([pill(("✓ " if s in done else "") + s, tone="success" if s in done else "info") for s in steps]),
    unsafe_allow_html=True,
)
st.markdown(f"**Acción recomendada:** {next_step}")

# Resumen Ejecutivo
st.subheader("Resumen del cliente")
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
    st.info("Aún faltan datos del proyecto. El asistente los irá captando.")
else:
    cols = st.columns(3)
    for idx, (label, value) in enumerate(summary_items):
        if not value:
            continue
        with cols[idx % 3]:
            st.markdown(f"**{label}**")
            st.write(value)

# Conversación con el chatbot
st.subheader("Conversación con el chatbot")
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

# Presupuesto
st.subheader("Presupuesto")
st.caption(f"Estado: {quote_status}")
pcols = st.columns(3)
pdf_key = f"_pdf_cache_{lead_id}"
if pcols[0].button("Descargar PDF", use_container_width=True):
    pdf = download_lead_pdf(str(lead_id), kind="comercial") or {}
    if isinstance(pdf, dict) and pdf.get("content"):
        st.session_state[pdf_key] = pdf
        st.rerun()

cached_pdf = st.session_state.get(pdf_key)
if isinstance(cached_pdf, dict) and cached_pdf.get("content"):
    st.download_button(
        "Descarga lista",
        data=cached_pdf["content"],
        file_name="presupuesto.pdf",
        mime=cached_pdf.get("content_type") or "application/pdf",
        use_container_width=True,
    )

if pcols[1].button("Reenviar por email", use_container_width=True):
    update_lead_panel(str(lead_id), quote_status="sent")
    st.success("Marcado como enviado.")

if pcols[2].button("Marcar como enviado", use_container_width=True):
    update_lead_panel(str(lead_id), quote_status="sent")
    st.success("Marcado como enviado.")

# Citas
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
            details = []
            if appt_date:
                details.append(f"{bucket}")
            if hour:
                details.append(f"{hour}")
            if tipo:
                details.append(tipo)
            details.append(human_status(status))
            st.caption(" · ".join([d for d in details if d]))

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

# Notas internas
st.subheader("Notas internas")
note_key = f"note_{lead_id}"
default_note = str(meta.get("internal_note") or "")
if note_key not in st.session_state:
    st.session_state[note_key] = default_note
st.text_area("Solo visible para tu negocio.", key=note_key, height=110, label_visibility="visible")
ncols = st.columns([0.25, 0.75])
if ncols[0].button("Guardar nota", use_container_width=True):
    update_lead_panel(str(lead_id), internal_note=st.session_state.get(note_key, ""))
    st.success("Nota guardada.")
ncols[1].caption("Ejemplos: “Llamar después de las 18h”, “Comparar con presupuesto anterior”.")
