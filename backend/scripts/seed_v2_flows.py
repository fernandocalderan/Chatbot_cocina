"""
Seed v2 flows (no IA)
=====================

Objetivo:
- Migrar tenants existentes a `branding.flow_system = "v2"` sin gastar cuota IA.
- Para cada tenant, crear un flow `published` en DB con el flujo efectivo actual (runtime),
  y apuntar `tenants.active_flow_id` a ese flow.

Uso:
  python3 backend/scripts/seed_v2_flows.py --dry-run
  python3 backend/scripts/seed_v2_flows.py --tenant-id <uuid>
  python3 backend/scripts/seed_v2_flows.py --limit 50
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.tenants import Tenant
from app.models.flows import Flow as FlowVersioned
from app.models.configs import Config
from app.services.flow_resolver import resolve_runtime_flow
from app.services.flow_templates import apply_materials
from app.services.verticals import resolve_flow_id


CONFIG_TIPO_MATERIALS = "tenant_flow_materials"


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


def _next_version(db: Session, tenant_id: str) -> int:
    latest = (
        db.query(FlowVersioned)
        .filter(FlowVersioned.tenant_id == tenant_id)
        .order_by(FlowVersioned.version.desc())
        .first()
    )
    return (latest.version + 1) if latest else 1


def _has_published_flow(db: Session, tenant: Tenant) -> bool:
    row = (
        db.query(FlowVersioned)
        .filter(FlowVersioned.tenant_id == tenant.id, FlowVersioned.estado == "published")
        .first()
    )
    return bool(row)


def seed_tenant(db: Session, tenant: Tenant, *, dry_run: bool, force: bool) -> tuple[bool, str]:
    branding = getattr(tenant, "branding", {}) or {}
    flow_system = str(branding.get("flow_system") or "v1").strip().lower()
    if flow_system == "v2" and getattr(tenant, "active_flow_id", None) and _has_published_flow(db, tenant) and not force:
        return True, "skip(already_v2)"

    materials = _load_published_materials(db, str(tenant.id))
    flow_id_override = materials.get("flow_id") if isinstance(materials, dict) else None
    flow_id_override = resolve_flow_id(flow_id_override, getattr(tenant, "vertical_key", None))
    plan_value = getattr(tenant, "plan", "base")
    if hasattr(plan_value, "value"):
        plan_value = plan_value.value

    flow_data = resolve_runtime_flow(
        db=db,
        tenant=tenant,
        flow_id_override=flow_id_override,
        plan_value=str(plan_value or "base").lower(),
    )
    flow_data = apply_materials(flow_data, materials)
    if not isinstance(flow_data, dict) or not flow_data:
        return False, "runtime_flow_not_available"

    if dry_run:
        return True, "dry_run(ok)"

    now = datetime.now(timezone.utc)
    new_flow = FlowVersioned(
        tenant_id=tenant.id,
        vertical_key=str(getattr(tenant, "vertical_key", "") or "") or None,
        version=_next_version(db, str(tenant.id)),
        schema_json=flow_data,
        estado="published",
        published_at=now,
    )
    db.add(new_flow)
    db.flush()

    tenant.active_flow_id = new_flow.id
    tenant.flow_mode = "VERTICAL"
    branding = getattr(tenant, "branding", {}) or {}
    branding["flow_system"] = "v2"
    branding["custom_flow_enabled"] = True
    tenant.branding = branding
    db.add(tenant)
    db.commit()
    return True, f"seeded(flow_id={new_flow.id}, v={new_flow.version})"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tenant-id", default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    db = SessionLocal()
    try:
        q = db.query(Tenant).order_by(Tenant.created_at.asc())
        if args.tenant_id:
            q = q.filter(Tenant.id == args.tenant_id)
        tenants = q.all()
        if args.limit and args.limit > 0:
            tenants = tenants[: args.limit]

        ok = 0
        fail = 0
        for t in tenants:
            success, msg = seed_tenant(db, t, dry_run=bool(args.dry_run), force=bool(args.force))
            if success:
                ok += 1
                print(f"[OK] tenant={t.id} {msg}")
            else:
                fail += 1
                print(f"[FAIL] tenant={t.id} {msg}")
        print(f"done ok={ok} fail={fail} dry_run={bool(args.dry_run)}")
        return 0 if fail == 0 else 2
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())

