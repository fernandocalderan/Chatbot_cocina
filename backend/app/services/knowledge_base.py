from __future__ import annotations

from pathlib import Path
from typing import Any

from loguru import logger
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.configs import Config
from app.models.files import FileAsset


CONFIG_TIPO_MATERIALS = "tenant_flow_materials"


def _latest_published_materials(db: Session, tenant_id: str) -> dict[str, Any] | None:
    try:
        rows = (
            db.query(Config)
            .filter(Config.tenant_id == tenant_id, Config.tipo == CONFIG_TIPO_MATERIALS)
            .order_by(Config.version.desc(), Config.updated_at.desc())
            .all()
        )
    except Exception:
        return None
    for row in rows:
        payload = row.payload_json or {}
        if str(payload.get("status") or "").upper() == "PUBLISHED":
            return payload if isinstance(payload, dict) else None
    return None


def tenant_knowledge_file_ids(db: Session, tenant_id: str) -> list[str]:
    payload = _latest_published_materials(db, tenant_id) or {}
    raw = payload.get("knowledge_files")
    if raw is None and isinstance(payload.get("content"), dict):
        raw = payload.get("content", {}).get("knowledge_files")
    if not isinstance(raw, list):
        return []
    out: list[str] = []
    seen: set[str] = set()
    for x in raw:
        fid = str(x).strip()
        if not fid or fid in seen:
            continue
        seen.add(fid)
        out.append(fid)
    return out


def build_knowledge_prompt(
    db: Session,
    tenant_id: str,
    *,
    max_files: int = 6,
    max_chars_per_file: int = 1200,
    max_total_chars: int = 6000,
) -> str:
    """
    Devuelve un bloque de texto que se puede inyectar en prompts IA.
    Usa solo archivos con `meta.extracted_text_key` (PDF auto-extraído o imagen extraída con IA).
    """
    file_ids = tenant_knowledge_file_ids(db, tenant_id)[:max_files]
    if not file_ids:
        return ""

    settings = get_settings()
    base_dir = Path(settings.storage_dir)

    parts: list[str] = []
    total = 0
    for fid in file_ids:
        asset = db.query(FileAsset).filter(FileAsset.id == fid, FileAsset.tenant_id == tenant_id).first()
        if not asset:
            continue
        meta = asset.meta or {}
        text_key = meta.get("extracted_text_key")
        if not text_key:
            continue
        path = base_dir / str(text_key)
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8").strip()
        except Exception as exc:
            logger.warning({"event": "knowledge_read_failed", "tenant_id": tenant_id, "file_id": fid, "error": str(exc)})
            continue
        if not text:
            continue
        text = text[:max_chars_per_file]
        name = meta.get("original_filename") or str(asset.s3_key).split("/")[-1]
        chunk = f"### {name}\n{text}\n"
        parts.append(chunk)
        total += len(chunk)
        if total >= max_total_chars:
            break

    out = "\n".join(parts).strip()
    return out[:max_total_chars]

