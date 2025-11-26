from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape
from loguru import logger

from app.services.file_service import FileService
from app.services.summary_service import SummaryService
from app.services.ai.openai_service import OpenAIService

try:
    from weasyprint import HTML
except Exception:  # pragma: no cover
    HTML = None

TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / "templates"


class PDFService:
    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader(str(TEMPLATE_ROOT)),
            autoescape=select_autoescape(["html", "xml"]),
        )
        self.file_service = FileService()
        self.summary_service = SummaryService()
        self.ai_service = OpenAIService()

    def render_pdf(self, template_path: str, context: Dict) -> bytes:
        template = self.env.get_template(template_path)
        html_content = template.render(**context)
        if HTML:
            try:
                return HTML(string=html_content).write_pdf()
            except Exception:
                pass
        return html_content.encode("utf-8")

    def _rewrite(self, text: str, tenant: Any, tone: str) -> str:
        plan = (
            getattr(tenant, "ia_plan", None) or getattr(tenant, "plan", "") or "base"
        ).lower()
        if plan not in {"pro", "elite"}:
            return text
        try:
            rewritten = self.ai_service.rewrite_for_pdf(
                text,
                tone=tone,
                tenant=tenant,
                tenant_id=str(getattr(tenant, "id", None)),
            )
            return rewritten or text
        except Exception:
            return text

    def _base_context(
        self, lead: Any, tenant: Any, extracted_data: Dict, ia_output: Dict
    ) -> Dict:
        return {
            "tenant_name": getattr(tenant, "name", "Tenant"),
            "cliente_nombre": (
                (getattr(lead, "meta_data", {}) or {}).get("contact_name")
                if lead
                else ""
            ),
            "estilo": extracted_data.get("style") or "",
            "metros": extracted_data.get("measures") or "",
            "presupuesto": extracted_data.get("budget") or "",
            "urgencia": extracted_data.get("urgency") or "",
            "extras": extracted_data.get("extras") or "",
            "images": extracted_data.get("images") or [],
            "resumen_ia": (
                ia_output.get("summary") if isinstance(ia_output, dict) else ""
            ),
            "fecha": extracted_data.get("fecha") or "",
        }

    def generate_commercial_pdf(
        self, lead: Any, tenant: Any, extracted_data: Dict, ia_output: Dict
    ) -> Dict:
        start = time.perf_counter()
        plan = (
            getattr(tenant, "ia_plan", None) or getattr(tenant, "plan", "") or "base"
        ).lower()
        ctx = self._base_context(lead, tenant, extracted_data, ia_output)
        if plan == "pro":
            ctx["resumen_ia"] = self._rewrite(
                ctx.get("resumen_ia") or "", tenant, tone="commercial"
            )
        elif plan == "elite":
            ctx["resumen_ia"] = self._rewrite(
                ctx.get("resumen_ia") or "", tenant, tone="commercial"
            )
            ctx["extras"] = ctx.get("extras") or ia_output.get("extras")
        template_path = (
            f"{plan}/comercial.html"
            if (TEMPLATE_ROOT / plan / "comercial.html").exists()
            else "base/comercial.html"
        )
        pdf_bytes = self.render_pdf(template_path, ctx)
        lead_id = str(getattr(lead, "id", getattr(lead, "lead_id", "")))
        key = self.file_service.upload_pdf(
            str(getattr(tenant, "id", "unknown")), lead_id, pdf_bytes, "comercial"
        )
        latency = (time.perf_counter() - start) * 1000
        logger.info(
            {
                "tenant_id": str(getattr(tenant, "id", None)),
                "lead_id": lead_id,
                "tipo_pdf": "comercial",
                "plan": plan,
                "success": True,
                "latency_ms": round(latency, 2),
                "s3_key": key,
            }
        )
        return {"pdf": pdf_bytes, "s3_key": key}

    def generate_operational_pdf(
        self, lead: Any, tenant: Any, extracted_data: Dict, ia_output: Dict
    ) -> Dict:
        start = time.perf_counter()
        plan = (
            getattr(tenant, "ia_plan", None) or getattr(tenant, "plan", "") or "base"
        ).lower()
        summary_text = self.summary_service.generate_operational_summary(
            lead, extracted_data, ia_output, tenant
        )
        ctx = self._base_context(lead, tenant, extracted_data, ia_output)
        ctx["resumen_ia"] = summary_text
        if plan in {"pro", "elite"}:
            ctx["resumen_ia"] = self._rewrite(
                ctx["resumen_ia"], tenant, tone="operational"
            )
        template_path = (
            f"{plan}/operativo.html"
            if (TEMPLATE_ROOT / plan / "operativo.html").exists()
            else "base/operativo.html"
        )
        pdf_bytes = self.render_pdf(template_path, ctx)
        lead_id = str(getattr(lead, "id", getattr(lead, "lead_id", "")))
        key = self.file_service.upload_pdf(
            str(getattr(tenant, "id", "unknown")), lead_id, pdf_bytes, "operativo"
        )
        latency = (time.perf_counter() - start) * 1000
        logger.info(
            {
                "tenant_id": str(getattr(tenant, "id", None)),
                "lead_id": lead_id,
                "tipo_pdf": "operativo",
                "plan": plan,
                "success": True,
                "latency_ms": round(latency, 2),
                "s3_key": key,
            }
        )
        return {"pdf": pdf_bytes, "s3_key": key}
