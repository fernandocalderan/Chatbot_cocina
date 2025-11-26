from __future__ import annotations

from typing import Any, Dict


class SummaryService:
    def generate_operational_summary(
        self, lead: Any, extracted_data: Dict, ia_output: Dict, tenant: Any
    ) -> str:
        plan = (
            getattr(tenant, "ia_plan", None) or getattr(tenant, "plan", "") or "base"
        ).lower()
        base_text = (
            f"Proyecto para {getattr(lead, 'meta_data', {}).get('contact_name', 'cliente')} "
            f"con estilo {extracted_data.get('style') or 'N/D'} y metros {extracted_data.get('measures') or 'N/D'}."
        )
        if plan == "base":
            return base_text
        brief = ia_output.get("summary") if isinstance(ia_output, dict) else None
        if plan == "pro":
            return f"{base_text} Nota IA: {brief or 'sin IA'}."
        extras = ia_output.get("extras") if isinstance(ia_output, dict) else None
        return f"{base_text} Resumen IA: {brief or 'sin IA'}. Extras: {extras or 'sin extras'}."
