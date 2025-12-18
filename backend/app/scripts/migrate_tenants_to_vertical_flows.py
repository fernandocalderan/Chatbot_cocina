from __future__ import annotations

import argparse
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.configs import Config
from app.models.flows import Flow as FlowVersioned
from app.models.tenants import Tenant
from app.services.flow_templates import apply_materials, load_flow_template
from app.services.verticals import get_vertical_config, provision_vertical_assets


CONFIG_TIPO_MATERIALS = "tenant_flow_materials"


def _norm_plan(plan) -> str:
    if hasattr(plan, "value"):
        plan = plan.value
    return str(plan or "base").strip().lower()


def _load_published_materials(db: Session, tenant_id: str) -> dict | None:
    rows = (
        db.query(Config)
        .filter(Config.tenant_id == tenant_id, Config.tipo == CONFIG_TIPO_MATERIALS)
        .order_by(Config.version.desc(), Config.updated_at.desc())
        .all()
    )
    for row in rows:
        payload = row.payload_json or {}
        if str(payload.get("status") or "").upper() == "PUBLISHED":
            return payload if isinstance(payload, dict) else None
    return None


def _latest_published_flow(db: Session, tenant_id: str) -> FlowVersioned | None:
    return (
        db.query(FlowVersioned)
        .filter(FlowVersioned.tenant_id == tenant_id, FlowVersioned.estado == "published")
        .order_by(FlowVersioned.published_at.desc().nullslast(), FlowVersioned.version.desc())
        .first()
    )


def _ensure_active_flow_id(db: Session, tenant: Tenant) -> bool:
    flow = _latest_published_flow(db, str(tenant.id))
    if not flow:
        return False
    changed = False
    if not getattr(tenant, "active_flow_id", None):
        tenant.active_flow_id = flow.id
        changed = True
    if not getattr(flow, "vertical_key", None) and getattr(tenant, "vertical_key", None):
        flow.vertical_key = str(tenant.vertical_key)
        db.add(flow)
        changed = True
    if getattr(tenant, "flow_mode", None) != "VERTICAL":
        tenant.flow_mode = "VERTICAL"
        changed = True
    if changed:
        db.add(tenant)
        db.commit()
    return True


def _create_published_flow_from_legacy(db: Session, tenant: Tenant) -> FlowVersioned | None:
    plan_value = _norm_plan(getattr(tenant, "plan", None))
    materials = _load_published_materials(db, str(tenant.id))
    vertical_key = getattr(tenant, "vertical_key", None)
    base = load_flow_template(
        None,
        plan_value=plan_value,
        vertical_key=str(vertical_key) if vertical_key else None,
    )
    base = apply_materials(base, materials)
    now = datetime.now(timezone.utc)
    latest = (
        db.query(FlowVersioned)
        .filter(FlowVersioned.tenant_id == tenant.id)
        .order_by(FlowVersioned.version.desc())
        .first()
    )
    next_version = (latest.version + 1) if latest else 1
    new_flow = FlowVersioned(
        tenant_id=tenant.id,
        vertical_key=str(tenant.vertical_key) if tenant.vertical_key else None,
        version=next_version,
        schema_json=base,
        estado="published",
        published_at=now,
    )
    db.add(new_flow)
    db.flush()
    tenant.active_flow_id = new_flow.id
    tenant.flow_mode = "VERTICAL"
    db.add(tenant)
    db.commit()
    return new_flow


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrar tenants a flows por tenant (vertical-based).")
    parser.add_argument("--default-vertical", default="kitchens")
    parser.add_argument("--apply", action="store_true", help="Aplica cambios en DB (si no, dry-run).")
    args = parser.parse_args()

    settings = get_settings()
    print(f"[migrate] DB={settings.database_url}")

    db = SessionLocal()
    try:
        tenants = db.query(Tenant).order_by(Tenant.created_at.asc()).all()
        print(f"[migrate] tenants={len(tenants)}")

        changed = 0
        created_flows = 0
        for tenant in tenants:
            tenant_id = str(tenant.id)
            had_vertical = bool(getattr(tenant, "vertical_key", None))
            vertical_key = getattr(tenant, "vertical_key", None) or args.default_vertical
            if not get_vertical_config(vertical_key):
                raise SystemExit(f"invalid_vertical_key: {vertical_key}")

            needs_update = (
                getattr(tenant, "vertical_key", None) != vertical_key
                or getattr(tenant, "flow_mode", None) != "VERTICAL"
                or not getattr(tenant, "active_flow_id", None)
            )
            flow = _latest_published_flow(db, tenant_id)
            flow_exists = bool(flow)

            if not args.apply:
                if needs_update or not flow_exists:
                    print(
                        f"[dry-run] tenant={tenant_id} name={tenant.name!r} vertical={vertical_key} "
                        f"had_vertical={had_vertical} has_flow={flow_exists} active_flow_id={getattr(tenant, 'active_flow_id', None)}"
                    )
                continue

            # Apply: set vertical + mode
            if getattr(tenant, "vertical_key", None) != vertical_key:
                tenant.vertical_key = vertical_key
                db.add(tenant)
                changed += 1
            if getattr(tenant, "flow_mode", None) != "VERTICAL":
                tenant.flow_mode = "VERTICAL"
                db.add(tenant)
                changed += 1
            db.commit()

            flow = _latest_published_flow(db, tenant_id)
            if not flow:
                # Create flow
                if had_vertical:
                    try:
                        created_info = provision_vertical_assets(db, tenant) or {}
                    except Exception:
                        db.rollback()
                        created_info = {}
                    flow = _latest_published_flow(db, tenant_id)
                    if flow:
                        created_flows += 1
                        print(f"[apply] created flow tenant={tenant_id} flow_id={flow.id} source=vertical info={created_info}")
                    else:
                        print(f"[warn] could not create flow for tenant={tenant_id} source=vertical")
                else:
                    created = _create_published_flow_from_legacy(db, tenant)
                    if created:
                        created_flows += 1
                        print(f"[apply] created flow tenant={tenant_id} flow_id={created.id} source=legacy")
                    else:
                        print(f"[warn] could not create flow for tenant={tenant_id} source=legacy")
            else:
                # Ensure active_flow_id and vertical_key on flow
                if _ensure_active_flow_id(db, tenant):
                    print(f"[apply] ensured active_flow_id tenant={tenant_id} active_flow_id={tenant.active_flow_id}")

            # Ensure other vertical assets (semantic/kpis/prompt/materials)
            try:
                provision_vertical_assets(db, tenant)
            except Exception:
                db.rollback()

        if args.apply:
            print(f"[done] updated_tenants={changed} created_flows={created_flows}")
        else:
            print("[done] dry-run")
        return 0
    finally:
        try:
            db.close()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
