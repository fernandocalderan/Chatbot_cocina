from __future__ import annotations

import os
from typing import Any

from loguru import logger
from openai import OpenAI
import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.files import FileAsset
from app.models.kb_chunks import KBChunk
from app.models.tenants import Tenant
from app.services.ia_usage_service import IAQuotaExceeded, IAUsageService


DEFAULT_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL") or "text-embedding-3-small"
DEFAULT_DIM = 1536


def _embed_query(db: Session, tenant: Tenant, query: str, *, model: str) -> list[float]:
    settings = get_settings()
    if not settings.openai_api_key:
        raise ValueError("missing_openai_api_key")

    # Estimación conservadora para enforce quota antes del request
    estimated_tokens = max(1, int(len((query or "").strip()) / 4) or 1)
    estimated_cost = IAUsageService.estimate_cost(model, estimated_tokens, 0)
    IAUsageService.enforce_quota(db, tenant, estimated_cost_next_call=max(estimated_cost, 0.0))

    client = OpenAI(api_key=settings.openai_api_key)
    resp = client.embeddings.create(model=model, input=[query])
    data = getattr(resp, "data", None) or []
    if not data:
        raise ValueError("embedding_empty")
    emb = getattr(data[0], "embedding", None)
    if not isinstance(emb, list) or len(emb) != DEFAULT_DIM:
        raise ValueError("embedding_invalid_dim")

    usage = getattr(resp, "usage", None)
    tokens_in = int(getattr(usage, "total_tokens", 0) or 0) if usage else 0
    try:
        IAUsageService.record_usage(
            db,
            str(tenant.id),
            model,
            tokens_in,
            0,
            IAUsageService.estimate_cost(model, tokens_in, 0),
            session_id=None,
            call_type="kb_query_embed",
        )
    except Exception:
        pass

    return emb


def search_kb(
    *,
    db: Session,
    tenant: Tenant,
    query: str,
    file_ids: list[str] | None = None,
    top_k: int = 6,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
) -> list[dict[str, Any]]:
    if not query.strip():
        return []
    try:
        qvec = _embed_query(db, tenant, query, model=embedding_model)
    except IAQuotaExceeded:
        raise
    except Exception as exc:
        logger.warning({"event": "kb_query_embed_failed", "tenant_id": str(tenant.id), "error": str(exc)})
        return []

    distance = KBChunk.embedding.cosine_distance(qvec).label("distance")
    q = (
        db.query(KBChunk, distance)
        .filter(KBChunk.tenant_id == tenant.id)
        .order_by(sa.asc(distance))
        .limit(max(1, min(int(top_k), 20)))
    )
    if file_ids:
        q = q.filter(KBChunk.file_id.in_(file_ids))

    rows = q.all()
    if not rows:
        return []

    file_id_set = {str(chunk.file_id) for chunk, _d in rows}
    files = (
        db.query(FileAsset)
        .filter(FileAsset.tenant_id == tenant.id, FileAsset.id.in_(list(file_id_set)))
        .all()
    )
    name_by_id = {str(f.id): ((f.meta or {}).get("original_filename") or str(f.s3_key).split("/")[-1]) for f in files}

    out: list[dict[str, Any]] = []
    for chunk, dist in rows:
        out.append(
            {
                "file_id": str(chunk.file_id),
                "filename": name_by_id.get(str(chunk.file_id)),
                "chunk_idx": int(chunk.chunk_idx),
                "distance": float(dist or 0.0),
                "text": chunk.text,
            }
        )
    return out


def format_kb_prompt(chunks: list[dict[str, Any]], *, max_chars: int = 6000) -> str:
    if not chunks:
        return ""
    parts: list[str] = []
    total = 0
    for item in chunks:
        name = item.get("filename") or item.get("file_id") or "Documento"
        text = str(item.get("text") or "").strip()
        if not text:
            continue
        block = f"### {name}\n{text}\n"
        parts.append(block)
        total += len(block)
        if total >= max_chars:
            break
    out = "\n".join(parts).strip()
    return out[:max_chars]

