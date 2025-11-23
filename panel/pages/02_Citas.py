import pandas as pd
import streamlit as st

from api_client import cancel_appointment, confirm_appointment, list_appointments
from auth import ensure_login
from utils import format_timestamp, load_styles

load_styles()
if "token" not in st.session_state:
    st.switch_page("auth.py")
ensure_login()

st.title("Citas")
st.caption("Gestiona citas y cambia su estado con confirmación/cancelación.")

appointments = list_appointments()

if not appointments:
    st.info("No hay citas disponibles.")
else:
    df_rows = []
    for appt in appointments:
        df_rows.append(
            {
                "slot_start": format_timestamp(appt.get("slot_start")),
                "slot_end": format_timestamp(appt.get("slot_end")),
                "visit_type": appt.get("visit_type") or "-",
                "lead_id": appt.get("lead_id") or "-",
                "status": appt.get("status"),
            }
        )

    df = pd.DataFrame(df_rows, columns=["slot_start", "slot_end", "visit_type", "lead_id", "status"])
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("Acciones")
    for i, appt in enumerate(appointments):
        col_info, col_confirm, col_cancel = st.columns([4, 2, 2])
        col_info.markdown(
            f"**{format_timestamp(appt.get('slot_start'))} → {format_timestamp(appt.get('slot_end'))}** "
            f"· Estado: `{appt.get('status')}` · Lead: `{appt.get('lead_id') or '-'}`"
        )
        if col_confirm.button("Confirmar", key=f"confirm_{i}"):
            res = confirm_appointment(appt.get("id"))
            if res:
                st.success("Cita confirmada")
                st.rerun()
        if col_cancel.button("Cancelar", key=f"cancel_{i}"):
            res = cancel_appointment(appt.get("id"))
            if res:
                st.warning("Cita cancelada")
                st.rerun()
