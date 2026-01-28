from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from sqlalchemy.orm import Session

from app.models.flows import Flow as FlowVersioned
from app.models.tenants import Tenant
from app.services.flow_templates import load_flow_template
from app.services.verticals import provision_vertical_assets
from app.services.verticals import tenant_custom_flow_enabled
from app.services.verticals import tenant_vertical_scopes
from app.services.subflows_composer import maybe_compose_for_tenant


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


def _active_or_latest_published_flow(db: Session, tenant: Tenant) -> FlowVersioned | None:
    tenant_id = str(getattr(tenant, "id"))
    active_id = getattr(tenant, "active_flow_id", None)
    if active_id:
        try:
            row = (
                db.query(FlowVersioned)
                .filter(
                    FlowVersioned.id == active_id,
                    FlowVersioned.tenant_id == tenant_id,
                    FlowVersioned.estado == "published",
                )
                .first()
            )
            if row:
                return row
        except Exception:
            return None

    row = _latest_published_flow(db, tenant_id)
    if row and not active_id:
        try:
            tenant.active_flow_id = row.id
            db.add(tenant)
            db.commit()
        except Exception:
            try:
                db.rollback()
            except Exception:
                pass
    return row


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
    Runtime flow resolver:
    1) Si el tenant es vertical y `custom_flow_enabled` es False -> usar SIEMPRE el flujo base (vertical + scopes).
    2) Si hay flujo publicado (tabla `flows`) y el custom está habilitado -> usarlo.
    3) Si el tenant tiene `vertical_key` y no hay flow publicado, intenta provisionar una vez (idempotente).
    4) Fallback conservador: carga template desde verticals/ o legacy app/flows (según `load_flow_template`).
    """
    vertical_key = getattr(tenant, "vertical_key", None)
    flow_system = _tenant_flow_system(tenant)

    flow_data: dict[str, Any] | None = None

    # v2: siempre preferir flow publicado en DB (si existe), sin depender de custom_flow_enabled.
    if flow_system == "v2":
        flow_row = _active_or_latest_published_flow(db, tenant)
        if flow_row and isinstance(flow_row.schema_json, dict):
            flow_data = flow_row.schema_json
        else:
            if vertical_key:
                try:
                    provision_vertical_assets(db, tenant)
                except Exception:
                    pass
                flow_row = _active_or_latest_published_flow(db, tenant)
                if flow_row and isinstance(flow_row.schema_json, dict):
                    flow_data = flow_row.schema_json
            if not flow_data:
                scopes = tenant_vertical_scopes(tenant)
                scope_key = str(scopes[0]).strip().lower() if scopes else None
                flow_data, _ = resolve_flow_for_scope(str(vertical_key), scope_key)
                if not flow_data:
                    flow_data = load_flow_template(
                        flow_id_override,
                        plan_value=plan_value,
                        vertical_key=str(vertical_key) if vertical_key else None,
                        scopes=scopes,
                    )
    else:
        # v1: comportamiento actual (respetar custom_flow_enabled para tenants verticales).
        if vertical_key and not tenant_custom_flow_enabled(tenant):
            scopes = tenant_vertical_scopes(tenant)
            scope_key = str(scopes[0]).strip().lower() if scopes else None
            flow_data, _ = resolve_flow_for_scope(str(vertical_key), scope_key)
            if not flow_data:
                flow_data = load_flow_template(
                    flow_id_override,
                    plan_value=plan_value,
                    vertical_key=str(vertical_key) if vertical_key else None,
                    scopes=scopes,
                )
        else:
            flow_row = _active_or_latest_published_flow(db, tenant)
            if flow_row and isinstance(flow_row.schema_json, dict):
                flow_data = flow_row.schema_json
            if not flow_data and vertical_key:
                try:
                    provision_vertical_assets(db, tenant)
                except Exception:
                    pass
                flow_row = _active_or_latest_published_flow(db, tenant)
                if flow_row and isinstance(flow_row.schema_json, dict):
                    flow_data = flow_row.schema_json
            if not flow_data:
                scopes = tenant_vertical_scopes(tenant)
                scope_key = str(scopes[0]).strip().lower() if scopes else None
                flow_data, _ = resolve_flow_for_scope(str(vertical_key), scope_key)
                if not flow_data:
                    flow_data = load_flow_template(
                        flow_id_override,
                        plan_value=plan_value,
                        vertical_key=str(vertical_key) if vertical_key else None,
                        scopes=scopes,
                    )

    if not isinstance(flow_data, dict):
        flow_data = {}
    try:
        flow_data = maybe_compose_for_tenant(db=db, tenant=tenant, base_flow=flow_data)
    except Exception:
        pass
    return flow_data
