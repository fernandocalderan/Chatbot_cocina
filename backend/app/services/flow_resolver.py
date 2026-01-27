from __future__ import annotations

from typing import Any

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
                flow_data = load_flow_template(
                    flow_id_override,
                    plan_value=plan_value,
                    vertical_key=str(vertical_key) if vertical_key else None,
                    scopes=tenant_vertical_scopes(tenant),
                )
    else:
        # v1: comportamiento actual (respetar custom_flow_enabled para tenants verticales).
        if vertical_key and not tenant_custom_flow_enabled(tenant):
            flow_data = load_flow_template(
                flow_id_override,
                plan_value=plan_value,
                vertical_key=str(vertical_key) if vertical_key else None,
                scopes=tenant_vertical_scopes(tenant),
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
                flow_data = load_flow_template(
                    flow_id_override,
                    plan_value=plan_value,
                    vertical_key=str(vertical_key) if vertical_key else None,
                    scopes=tenant_vertical_scopes(tenant),
                )

    if not isinstance(flow_data, dict):
        flow_data = {}
    try:
        flow_data = maybe_compose_for_tenant(db=db, tenant=tenant, base_flow=flow_data)
    except Exception:
        pass
    return flow_data
