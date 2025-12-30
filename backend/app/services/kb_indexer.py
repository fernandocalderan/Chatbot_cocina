from __future__ import annotations

import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loguru import logger
from openai import APIConnectionError, APIStatusError, AuthenticationError, OpenAI, RateLimitError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.kb_chunks import KBChunk
from app.models.files import FileAsset
from app.models.tenants import Tenant
from app.services.ia_usage_service import IAQuotaExceeded, IAUsageService


DEFAULT_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL") or "text-embedding-3-small"
DEFAULT_DIM = 1536  # text-embedding-3-small


def _estimate_tokens(text: str) -> int:
    # Aproximación conservadora (sin tiktoken): ~4 chars/token
    return max(1, int(math.ceil(len((text or "").strip()) / 4.0)))


def _chunk_text(text: str, *, max_chars: int = 1200, overlap: int = 150, max_chunks: int = 200) -> list[str]:
    raw = (text or "").strip().replace("\r\n", "\n")
    if not raw:
        return []

    paragraphs = [p.strip() for p in raw.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [raw]

    chunks: list[str] = []
    buf = ""
    for p in paragraphs:
        candidate = (buf + "\n\n" + p).strip() if buf else p
        if len(candidate) <= max_chars:
            buf = candidate
            continue
        if buf:
            chunks.append(buf)
            if len(chunks) >= max_chunks:
                return chunks
        # si un párrafo es enorme, cortar duro
        if len(p) > max_chars:
            start = 0
            while start < len(p) and len(chunks) < max_chunks:
                end = min(start + max_chars, len(p))
                chunks.append(p[start:end].strip())
                start = max(0, end - overlap)
            buf = ""
        else:
            buf = p

    if buf and len(chunks) < max_chunks:
        chunks.append(buf)

    # overlap entre chunks (suave) para continuidad
    if overlap and len(chunks) > 1:
        overlapped: list[str] = []
        for i, c in enumerate(chunks):
            if i == 0:
                overlapped.append(c)
                continue
            prev = chunks[i - 1]
            tail = prev[-overlap:] if len(prev) > overlap else prev
            overlapped.append((tail + "\n" + c).strip())
        chunks = overlapped

    return [c for c in chunks if c]


def _read_extracted_text(asset: FileAsset) -> str:
    meta = asset.meta or {}
    text_key = meta.get("extracted_text_key")
    if not text_key:
        return ""
    settings = get_settings()
    base_dir = Path(settings.storage_dir)
    path = base_dir / str(text_key)
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8").strip()
    except Exception:
        return ""


def index_file(
    *,
    db: Session,
    tenant: Tenant,
    file_id: str,
    reindex: bool = False,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    max_chunks: int = 160,
) -> dict[str, Any]:
    asset = db.query(FileAsset).filter(FileAsset.id == file_id, FileAsset.tenant_id == tenant.id).first()
    if not asset:
        raise ValueError("file_not_found")

    text = _read_extracted_text(asset)
    if not text:
        raise ValueError("file_not_extracted")

    if not reindex:
        existing = db.query(KBChunk).filter(KBChunk.tenant_id == tenant.id, KBChunk.file_id == asset.id).first()
        if existing:
            return {"file_id": str(asset.id), "indexed": True, "skipped": True, "chunks": None}

    chunks = _chunk_text(text, max_chunks=max_chunks)
    if not chunks:
        raise ValueError("no_chunks")

    # Enforce quota antes de embeddings (estimación conservadora)
    approx_tokens = sum(_estimate_tokens(c) for c in chunks)
    estimated_cost = IAUsageService.estimate_cost(embedding_model, approx_tokens, 0)
    try:
        IAUsageService.enforce_quota(db, tenant, estimated_cost_next_call=max(estimated_cost, 0.0))
    except IAQuotaExceeded as exc:
        raise IAQuotaExceeded(str(exc))

    settings = get_settings()
    if not settings.openai_api_key:
        raise ValueError("missing_openai_api_key")

    client = OpenAI(api_key=settings.openai_api_key)

    # Limpiar chunks previos
    db.query(KBChunk).filter(KBChunk.tenant_id == tenant.id, KBChunk.file_id == asset.id).delete()
    db.commit()

    try:
        resp = client.embeddings.create(model=embedding_model, input=chunks)
        data = getattr(resp, "data", None) or []
        usage = getattr(resp, "usage", None)
        tokens_in = int(getattr(usage, "total_tokens", 0) or 0) if usage else 0
        tokens_out = 0
        cost = IAUsageService.estimate_cost(embedding_model, tokens_in, tokens_out)
        try:
            IAUsageService.record_usage(
                db,
                str(tenant.id),
                embedding_model,
                tokens_in,
                tokens_out,
                cost,
                session_id=None,
                call_type="kb_embed",
            )
        except Exception:
            pass

        now = datetime.now(timezone.utc)
        rows: list[KBChunk] = []
        for i, item in enumerate(data):
            emb = getattr(item, "embedding", None)
            if not isinstance(emb, list) or len(emb) != DEFAULT_DIM:
                continue
            rows.append(
                KBChunk(
                    tenant_id=tenant.id,
                    file_id=asset.id,
                    chunk_idx=i,
                    text=chunks[i],
                    embedding=emb,
                    meta={
                        "embedding_model": embedding_model,
                        "original_filename": (asset.meta or {}).get("original_filename"),
                    },
                    created_at=now,
                )
            )
        if not rows:
            raise ValueError("embedding_failed")
        db.add_all(rows)
        db.commit()

        meta = asset.meta or {}
        meta["kb_indexed_at"] = now.isoformat()
        meta["kb_index_model"] = embedding_model
        meta["kb_chunks"] = len(rows)
        asset.meta = meta
        db.add(asset)
        db.commit()
        return {"file_id": str(asset.id), "indexed": True, "skipped": False, "chunks": len(rows)}
    except AuthenticationError as exc:
        logger.warning(
            {
                "event": "kb_index_failed",
                "tenant_id": str(tenant.id),
                "file_id": str(asset.id),
                "error": "invalid_openai_api_key",
            }
        )
        raise ValueError("invalid_openai_api_key") from exc
    except RateLimitError as exc:
        logger.warning(
            {
                "event": "kb_index_failed",
                "tenant_id": str(tenant.id),
                "file_id": str(asset.id),
                "error": "ia_rate_limited",
            }
        )
        raise ValueError("ia_rate_limited") from exc
    except APIConnectionError as exc:
        logger.warning(
            {
                "event": "kb_index_failed",
                "tenant_id": str(tenant.id),
                "file_id": str(asset.id),
                "error": "ia_provider_unavailable",
            }
        )
        raise ValueError("ia_provider_unavailable") from exc
    except APIStatusError as exc:
        # 5xx del provider → degradado temporal
        logger.warning(
            {
                "event": "kb_index_failed",
                "tenant_id": str(tenant.id),
                "file_id": str(asset.id),
                "error": f"ia_provider_error:{getattr(exc, 'status_code', None) or 'unknown'}",
            }
        )
        raise ValueError("ia_provider_unavailable") from exc
    except Exception as exc:
        logger.warning({"event": "kb_index_failed", "tenant_id": str(tenant.id), "file_id": str(asset.id), "error": str(exc)})
        raise
