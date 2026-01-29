from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session
import sqlalchemy as sa

from app.models.flows import Flow as FlowVersioned

EXIT_KEYWORDS = {"volver", "inicio", "menu", "salir"}
WORD_RE = re.compile(r"[a-zA-Z0-9_\-]+")


@dataclass(slots=True)
class SubflowCandidate:
    flow: FlowVersioned
    score: int
    matched: list[str]


def normalize_keywords(raw: Any) -> list[str]:
    if not raw:
        return []
    items: list[str] = []
    if isinstance(raw, str):
        raw = raw.strip()
        if not raw:
            return []
        if raw.startswith("["):
            try:
                loaded = __import__("json").loads(raw)
                if isinstance(loaded, list):
                    items = [str(x) for x in loaded if x]
            except Exception:
                items = []
        if not items:
            items = [s.strip() for s in raw.split(",") if s.strip()]
    elif isinstance(raw, list):
        items = [str(x) for x in raw if x]
    else:
        return []

    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        key = str(item or "").strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def _normalize_text(text: str) -> tuple[str, set[str]]:
    cleaned = " ".join(WORD_RE.findall(text.lower()))
    tokens = set(cleaned.split()) if cleaned else set()
    return cleaned, tokens


def _exit_requested(text: str) -> bool:
    cleaned, tokens = _normalize_text(text)
    if not cleaned:
        return False
    for keyword in EXIT_KEYWORDS:
        if keyword in tokens or keyword in cleaned:
            return True
    return False


def _match_keywords(text: str, tokens: set[str], keywords: list[str]) -> list[str]:
    matched: list[str] = []
    for kw in keywords:
        kw_norm = str(kw or "").strip().lower()
        if not kw_norm:
            continue
        if " " in kw_norm:
            if kw_norm in text:
                matched.append(kw_norm)
        else:
            if kw_norm in tokens:
                matched.append(kw_norm)
    return matched


def _query_published_subflows(db: Session, *, base_flow_id: str) -> sa.orm.Query:
    return db.query(FlowVersioned).filter(
        FlowVersioned.flow_kind == "subflow",
        FlowVersioned.parent_flow_id == base_flow_id,
        FlowVersioned.estado == "published",
        FlowVersioned.archived.is_(False),
    )


def list_published_subflows(
    db: Session, *, tenant_id: str | None, base_flow_id: str
) -> tuple[list[FlowVersioned], str]:
    q = _query_published_subflows(db, base_flow_id=base_flow_id)
    tenant_flows: list[FlowVersioned] = []
    if tenant_id:
        tenant_flows = (
            q.filter(FlowVersioned.owner_type == "TENANT", FlowVersioned.owner_id == tenant_id).all()
        )
    if tenant_flows:
        return tenant_flows, "TENANT"

    global_flows = (
        q.filter(FlowVersioned.owner_type == "GLOBAL", FlowVersioned.owner_id.is_(None)).all()
    )
    return global_flows, "GLOBAL"


def pick_subflow(
    *,
    db: Session,
    tenant_id: str | None,
    base_flow_id: str,
    user_text: str,
    active_subflow_id: str | None = None,
) -> dict[str, Any]:
    result = {
        "picked": None,
        "candidates": [],
        "action": "none",
        "matched": [],
        "source": None,
    }
    text = str(user_text or "").strip()
    if not text:
        return result

    if _exit_requested(text):
        result["action"] = "exit"
        return result

    if active_subflow_id:
        active = (
            db.query(FlowVersioned)
            .filter(
                FlowVersioned.id == active_subflow_id,
                FlowVersioned.flow_kind == "subflow",
                FlowVersioned.estado == "published",
                FlowVersioned.archived.is_(False),
            )
            .first()
        )
        if active and isinstance(active.schema_json, dict):
            result["picked"] = active
            result["action"] = "keep_active"
            result["source"] = str(getattr(active, "owner_type", "")) or None
            return result

    flows, source = list_published_subflows(db, tenant_id=tenant_id, base_flow_id=base_flow_id)
    if not flows:
        return result

    text_norm, tokens = _normalize_text(text)
    candidates: list[SubflowCandidate] = []
    for flow in flows:
        keywords = normalize_keywords(getattr(flow, "trigger_keywords", None))
        if not keywords:
            continue
        matched = _match_keywords(text_norm, tokens, keywords)
        score = len(matched)
        threshold = int(getattr(flow, "trigger_threshold", 1) or 1)
        if score >= threshold:
            candidates.append(SubflowCandidate(flow=flow, score=score, matched=matched))

    if not candidates:
        return result

    def _sort_key(item: SubflowCandidate) -> tuple[int, int, datetime]:
        priority = int(getattr(item.flow, "trigger_priority", 0) or 0)
        published_at = getattr(item.flow, "published_at", None) or datetime.min
        return (priority, item.score, published_at)

    candidates_sorted = sorted(candidates, key=_sort_key, reverse=True)
    picked = candidates_sorted[0]

    result["picked"] = picked.flow
    result["action"] = "picked"
    result["matched"] = picked.matched
    result["source"] = source
    result["candidates"] = [
        {
            "flow_id": str(c.flow.id),
            "subflow_key": getattr(c.flow, "subflow_key", None),
            "score": c.score,
            "priority": int(getattr(c.flow, "trigger_priority", 0) or 0),
            "threshold": int(getattr(c.flow, "trigger_threshold", 1) or 1),
            "owner_type": getattr(c.flow, "owner_type", None),
        }
        for c in candidates_sorted
    ]
    return result


def simulate_subflow_routing(
    *, db: Session, tenant_id: str | None, base_flow_id: str, user_text: str
) -> dict[str, Any]:
    route = pick_subflow(
        db=db,
        tenant_id=tenant_id,
        base_flow_id=base_flow_id,
        user_text=user_text,
        active_subflow_id=None,
    )
    picked = None
    if route.get("picked") is not None:
        flow = route["picked"]
        picked = {
            "flow_id": str(flow.id),
            "subflow_key": getattr(flow, "subflow_key", None),
            "owner_type": getattr(flow, "owner_type", None),
            "matched": route.get("matched") or [],
        }
    return {
        "picked": picked,
        "candidates": route.get("candidates") or [],
    }
