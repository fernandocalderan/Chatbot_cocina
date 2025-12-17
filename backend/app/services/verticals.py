from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.db.session import SessionLocal
from app.models.configs import Config
from app.models.tenants import Tenant
from app.services.flow_templates import list_flow_templates


_REGISTRY_PATH = Path(__file__).resolve().parent.parent / "verticals" / "registry.json"


def _load_registry() -> dict[str, Any]:
    if _REGISTRY_PATH.exists():
        with _REGISTRY_PATH.open() as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    return {}


def list_verticals() -> list[dict[str, str]]:
    registry = _load_registry()
    items = []
    for key, cfg in registry.items():
        label = cfg.get("label") or key.replace("_", " ").title()
        items.append({"key": key, "label": label})
    return items


def get_vertical_config(vertical_key: str | None) -> dict[str, Any]:
    if not vertical_key:
        return {}
    registry = _load_registry()
    return registry.get(vertical_key, {}) if isinstance(registry, dict) else {}


def allowed_flow_ids(vertical_key: str | None) -> list[str]:
    cfg = get_vertical_config(vertical_key)
    flow_ids = cfg.get("flow_ids")
    if isinstance(flow_ids, list) and flow_ids:
        return [str(f) for f in flow_ids]
    default_flow = cfg.get("default_flow_id")
    return [str(default_flow)] if default_flow else []


def default_flow_id(vertical_key: str | None) -> str | None:
    cfg = get_vertical_config(vertical_key)
    default_id = cfg.get("default_flow_id")
    if default_id:
        return str(default_id)
    flow_ids = allowed_flow_ids(vertical_key)
    return flow_ids[0] if flow_ids else None


def resolve_flow_id(flow_id: str | None, vertical_key: str | None) -> str | None:
    if not vertical_key:
        return flow_id
    allowed = allowed_flow_ids(vertical_key)
    if flow_id and (not allowed or flow_id in allowed):
        return flow_id
    return default_flow_id(vertical_key) or flow_id


def list_flow_templates_for_vertical(vertical_key: str | None) -> list[dict[str, str]]:
    allowed = set(allowed_flow_ids(vertical_key))
    return list_flow_templates(allowed_ids=allowed if allowed else None)


def vertical_prompt(vertical_key: str | None) -> str | None:
    cfg = get_vertical_config(vertical_key)
    prompt = cfg.get("vertical_prompt")
    return str(prompt) if prompt else None


def provision_vertical_materials(db, tenant: Tenant) -> dict | None:
    if not tenant or not tenant.vertical_key:
        return None
    existing = (
        db.query(Config)
        .filter(Config.tenant_id == tenant.id, Config.tipo == "tenant_flow_materials")
        .order_by(Config.version.desc())
        .first()
    )
    if existing:
        return existing.payload_json or {}
    flow_id = resolve_flow_id(None, tenant.vertical_key)
    payload = {
        "flow_id": flow_id,
        "content": {
            "welcome": "",
            "questions": {},
            "buttons": {},
            "errors": {},
            "closing": "",
            "language": tenant.idioma_default or "es",
            "tone": "serio",
        },
        "automation": {
            "ai_level": "medium",
            "saving_mode": False,
            "human_fallback": True,
            "max_response_seconds": 8,
            "ai_steps": [],
        },
        "status": "PUBLISHED",
    }
    db.add(
        Config(
            tenant_id=tenant.id,
            tipo="tenant_flow_materials",
            version=1,
            payload_json=payload,
        )
    )
    db.commit()
    return payload


def fetch_tenant_vertical_key(tenant_id: str | None) -> str | None:
    if not tenant_id:
        return None
    session = SessionLocal()
    try:
        tenant = session.query(Tenant).filter(Tenant.id == tenant_id).first()
        return str(tenant.vertical_key) if tenant and tenant.vertical_key else None
    finally:
        session.close()
