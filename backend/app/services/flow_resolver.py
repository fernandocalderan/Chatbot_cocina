from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
import logging
import json

from sqlalchemy.orm import Session

from app.models.flows import Flow as FlowVersioned
from app.models.tenant_flow_overrides import TenantFlowOverride
from app.models.tenants import Tenant
from app.services.subflows_composer import maybe_compose_for_tenant
from app.services.verticals import tenant_vertical_scopes

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ResolvedFlow:
    id: str
    version: int | None
    estado: str
    published_at: datetime | None
    schema_json: dict[str, Any]
    source: str
    base_flow_id: str | None = None


class FlowResolutionError(RuntimeError):
    def __init__(self, code: str, detail: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail


def _tenant_flow_system(tenant: Tenant | None) -> str:
    """
    v1 (legacy): respeta `branding.custom_flow_enabled` para tenants con vertical.
    v2: siempre intenta usar flow publicado en DB; si no existe, fallback a vertical+scopes.
    """
    if not tenant:
        return "v1"
    branding = getattr(tenant, "branding", {}) or {}
    val = branding.get("flow_system")
    return str(val or "v1").strip().lower()


def _latest_published_flow(db: Session, tenant_id: str) -> FlowVersioned | None:
    try:
        return (
            db.query(FlowVersioned)
            .filter(FlowVersioned.tenant_id == tenant_id, FlowVersioned.estado == "published")
            .order_by(FlowVersioned.published_at.desc().nullslast(), FlowVersioned.version.desc())
            .first()
        )
    except Exception:
        return None


def _latest_published_template(
    db: Session, *, vertical_key: str | None, scope_key: str | None, flow_kind: str
) -> FlowVersioned | None:
    if not vertical_key or not scope_key:
        return None
    try:
        return (
            db.query(FlowVersioned)
            .filter(
                FlowVersioned.owner_type == "GLOBAL",
                FlowVersioned.owner_id.is_(None),
                FlowVersioned.estado == "published",
                FlowVersioned.vertical_key == vertical_key,
                FlowVersioned.scope_key == scope_key,
                FlowVersioned.flow_kind == flow_kind,
            )
            .order_by(FlowVersioned.published_at.desc().nullslast(), FlowVersioned.version.desc())
            .first()
        )
    except Exception:
        return None


def _published_override(
    db: Session, *, tenant_id: str, base_flow_id: str
) -> TenantFlowOverride | None:
    try:
        return (
            db.query(TenantFlowOverride)
            .filter(
                TenantFlowOverride.tenant_id == tenant_id,
                TenantFlowOverride.base_flow_id == base_flow_id,
                TenantFlowOverride.published.is_(True),
            )
            .order_by(TenantFlowOverride.published_at.desc().nullslast(), TenantFlowOverride.updated_at.desc())
            .first()
        )
    except Exception:
        return None


def resolve_active_flow(
    db: Session,
    tenant_id: str,
    *,
    tenant: Tenant | None = None,
    vertical_key: str | None = None,
    scope_key: str | None = None,
    flow_kind: str = "base",
) -> ResolvedFlow:
    """
    Resolver único y determinista:
    - Filtra por tenant_id y estado=published
    - Ordena por published_at DESC, version DESC
    - Si no hay flujo publicado → error explícito
    - Si hay más de uno → error explícito (integridad)
    """
    if not tenant:
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    vertical_key = vertical_key or (getattr(tenant, "vertical_key", None) if tenant else None)
    scope_key = scope_key or (tenant_vertical_scopes(tenant)[0] if tenant and tenant_vertical_scopes(tenant) else None)

    template = _latest_published_template(db, vertical_key=vertical_key, scope_key=scope_key, flow_kind=flow_kind)
    if template:
        override = _published_override(db, tenant_id=str(tenant_id), base_flow_id=str(template.id))
        if override and isinstance(override.draft_json, dict):
            version = int(override.published_at.timestamp()) if override.published_at else None
            return ResolvedFlow(
                id=str(override.flow_id),
                version=version,
                estado="published",
                published_at=override.published_at,
                schema_json=override.draft_json,
                source="TENANT_OVERRIDE",
                base_flow_id=str(template.id),
            )

    # Legacy tenant published flows (override implicit)
    tenant_flow = _latest_published_flow(db, tenant_id)
    if tenant_flow and isinstance(tenant_flow.schema_json, dict):
        return ResolvedFlow(
            id=str(tenant_flow.id),
            version=tenant_flow.version,
            estado=tenant_flow.estado,
            published_at=tenant_flow.published_at,
            schema_json=tenant_flow.schema_json,
            source="TENANT_FLOW",
        )

    if template and isinstance(template.schema_json, dict):
        return ResolvedFlow(
            id=str(template.id),
            version=template.version,
            estado=template.estado,
            published_at=template.published_at,
            schema_json=template.schema_json,
            source="GLOBAL_TEMPLATE",
        )

    raise FlowResolutionError("no_published_flow", f"tenant={tenant_id} has no published flow")


def _active_or_latest_published_flow(db: Session, tenant: Tenant) -> FlowVersioned | None:
    tenant_id = str(getattr(tenant, "id"))
    return _latest_published_flow(db, tenant_id)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _deep_merge(base_obj: dict[str, Any], override_obj: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = dict(base_obj)
    for k, v in override_obj.items():
        if isinstance(v, dict) and isinstance(merged.get(k), dict):
            merged[k] = _deep_merge(merged.get(k, {}), v)
        else:
            merged[k] = v
    return merged


def resolve_flow_for_scope(
    vertical_key: str | None,
    scope_key: str | None,
    *,
    base_dir: Path | None = None,
) -> tuple[dict[str, Any], str | None]:
    """
    Resuelve el flow base por scope (filesystem).
    Prioridad:
      1) flow_base_scope_<scope>.json
      2) flow_scope_<scope>.json (legacy)
      3) flow_overrides en metadata.json
      4) flow_base.json
    """
    if not vertical_key:
        return {}, None
    vkey = str(vertical_key).strip()
    vdir = (base_dir or (Path(__file__).resolve().parent.parent / "verticals")) / vkey
    base_path = vdir / "flow_base.json"
    if not base_path.exists():
        return {}, None
    base = _read_json(base_path)

    skey = str(scope_key or "").strip().lower()
    if skey:
        scoped = vdir / f"flow_base_scope_{skey}.json"
        legacy = vdir / f"flow_scope_{skey}.json"
        if scoped.exists():
            return _read_json(scoped), str(scoped)
        if legacy.exists():
            return _read_json(legacy), str(legacy)
        meta_path = vdir / "metadata.json"
        if meta_path.exists():
            meta = _read_json(meta_path)
            defs = meta.get("scope_definitions") if isinstance(meta.get("scope_definitions"), dict) else {}
            entry = defs.get(skey) if isinstance(defs.get(skey), dict) else {}
            overrides = entry.get("flow_overrides") if isinstance(entry, dict) else None
            if isinstance(overrides, dict) and overrides:
                return _deep_merge(base, overrides), "metadata.flow_overrides"
    return base, str(base_path)


def resolve_runtime_flow(
    *,
    db: Session,
    tenant: Tenant,
    flow_id_override: str | None,
    plan_value: str | None,
) -> dict[str, Any]:
    """
    Resolver único y determinista:
    - Usa SIEMPRE el flujo publicado activo del tenant.
    - Si no existe un published flow, lanza error explícito (sin fallback).
    """
    vertical_key = getattr(tenant, "vertical_key", None)
    flow_data: dict[str, Any] | None = None
    tenant_id = str(getattr(tenant, "id"))
    flow_row = resolve_active_flow(db, tenant_id, tenant=tenant, flow_kind=str(plan_value or "base").lower())
    if not flow_row or not isinstance(flow_row.schema_json, dict):
        raise FlowResolutionError("invalid_published_flow", f"tenant={tenant_id} published flow invalid")
    flow_data = flow_row.schema_json
    try:
        flow_data = maybe_compose_for_tenant(db=db, tenant=tenant, base_flow=flow_data)
    except Exception:
        pass
    logger.info(
        f\"Resolved active flow → tenant={tenant_id} source={getattr(flow_row,'source','unknown')} flow={flow_row.id} version={flow_row.version} published_at={flow_row.published_at}\"
    )
    return flow_data
