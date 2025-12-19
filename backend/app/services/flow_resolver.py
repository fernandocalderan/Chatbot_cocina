from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.flows import Flow as FlowVersioned
from app.models.tenants import Tenant
from app.services.flow_templates import load_flow_template
from app.services.verticals import provision_vertical_assets
from app.services.verticals import tenant_custom_flow_enabled
from app.services.verticals import tenant_vertical_scopes


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
    if vertical_key and not tenant_custom_flow_enabled(tenant):
        return load_flow_template(
            flow_id_override,
            plan_value=plan_value,
            vertical_key=str(vertical_key) if vertical_key else None,
            scopes=tenant_vertical_scopes(tenant),
        )

    flow_row = _active_or_latest_published_flow(db, tenant)
    if flow_row and isinstance(flow_row.schema_json, dict):
        return flow_row.schema_json

    if vertical_key:
        try:
            provision_vertical_assets(db, tenant)
        except Exception:
            pass
        flow_row = _active_or_latest_published_flow(db, tenant)
        if flow_row and isinstance(flow_row.schema_json, dict):
            return flow_row.schema_json

    return load_flow_template(
        flow_id_override,
        plan_value=plan_value,
        vertical_key=str(vertical_key) if vertical_key else None,
        scopes=tenant_vertical_scopes(tenant),
    )
