from __future__ import annotations

import base64
from pathlib import Path

from loguru import logger

from app.core.config import get_settings
from app.models.tenants import Tenant
from app.services.ia_usage_service import IAQuotaExceeded, IAUsageService


def _read_bytes(path: Path) -> bytes:
    with path.open("rb") as f:
        return f.read()


def extract_pdf_text(path: Path, *, max_chars: int = 50_000) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception:
        logger.warning({"event": "pdf_extract_missing_dep", "path": str(path)})
        return ""

    try:
        reader = PdfReader(str(path))
        chunks: list[str] = []
        for page in reader.pages[:50]:
            try:
                text = page.extract_text() or ""
            except Exception:
                text = ""
            if text:
                chunks.append(text)
            if sum(len(c) for c in chunks) >= max_chars:
                break
        out = "\n\n".join(chunks).strip()
        return out[:max_chars]
    except Exception as exc:
        logger.warning({"event": "pdf_extract_failed", "path": str(path), "error": str(exc)})
        return ""


def extract_image_text_via_openai(
    path: Path,
    *,
    content_type: str,
    tenant: Tenant,
    tenant_id: str,
    db,
    session_id: str | None = None,
    max_chars: int = 20_000,
) -> str:
    settings = get_settings()
    api_key = settings.openai_api_key
    if not api_key:
        return ""

    try:
        from openai import OpenAI  # type: ignore
    except Exception:
        return ""

    raw = _read_bytes(path)
    b64 = base64.b64encode(raw).decode("ascii")
    data_url = f"data:{content_type};base64,{b64}"

    prompt = (
        "Extrae el texto visible de esta imagen (si existe) y describe brevemente el contenido. "
        "Devuelve texto plano en español."
    )

    model = settings.ai_model or "gpt-4.1-mini"

    # Enforce quota antes de llamar
    try:
        IAUsageService.enforce_quota(db, tenant, estimated_cost_next_call=0.0)
    except IAQuotaExceeded:
        return ""

    client = OpenAI(api_key=api_key)
    try:
        completion = client.chat.completions.create(
            model=model,
            temperature=0.1,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            ],
        )
        text = (completion.choices[0].message.content or "").strip()
        usage = getattr(completion, "usage", None)
        tokens_in = int(getattr(usage, "prompt_tokens", 0) or 0) if usage else 0
        tokens_out = int(getattr(usage, "completion_tokens", 0) or 0) if usage else 0
        cost = IAUsageService.estimate_cost(model, tokens_in, tokens_out)
        try:
            IAUsageService.record_usage(
                db,
                tenant_id,
                model,
                tokens_in,
                tokens_out,
                cost,
                session_id=session_id,
                call_type="file_extract_image",
            )
        except Exception:
            pass
        return text[:max_chars]
    except Exception as exc:
        logger.warning({"event": "image_extract_failed", "path": str(path), "error": str(exc)})
        return ""


def write_extracted_text(dest_path: Path, text: str) -> Path | None:
    if not text:
        return None
    out_path = dest_path.parent / f"{dest_path.stem}.extracted.txt"
    try:
        out_path.write_text(text, encoding="utf-8")
        return out_path
    except Exception as exc:
        logger.warning({"event": "extract_write_failed", "path": str(out_path), "error": str(exc)})
        return None


def preview(text: str, *, max_chars: int = 800) -> str:
    text = (text or "").strip().replace("\r\n", "\n")
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "…"
