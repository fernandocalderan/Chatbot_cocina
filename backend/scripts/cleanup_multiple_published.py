from __future__ import annotations

import argparse
from datetime import datetime, timezone
from collections import defaultdict

from sqlalchemy.exc import OperationalError

from app.db.session import SessionLocal
from app.models.flows import Flow
from app.models.tenants import Tenant


def _pick_primary_scope(tenant: Tenant | None) -> str:
    if not tenant:
        return "unknown"
    branding = getattr(tenant, "branding", {}) or {}
    raw = branding.get("vertical_scopes") or []
    if isinstance(raw, list) and raw:
        return str(raw[0])
    return "unknown"


def _winner_key(flow: Flow) -> tuple[datetime, datetime, datetime, int]:
    published_at = flow.published_at or datetime.min.replace(tzinfo=timezone.utc)
    updated_at = flow.updated_at or datetime.min.replace(tzinfo=timezone.utc)
    created_at = flow.created_at or datetime.min.replace(tzinfo=timezone.utc)
    return (published_at, updated_at, created_at, int(flow.version or 0))


def cleanup(*, apply: bool) -> int:
    db = SessionLocal()
    try:
        tenants = {str(t.id): t for t in db.query(Tenant).all()}
        published_flows = (
            db.query(Flow)
            .filter(Flow.estado == "published")
            .all()
        )
        groups: dict[tuple[str, str, str], list[Flow]] = defaultdict(list)
        for flow in published_flows:
            tenant = tenants.get(str(flow.tenant_id))
            vertical_key = (flow.vertical_key or getattr(tenant, "vertical_key", None) or "unknown").strip()
            scope_key = _pick_primary_scope(tenant)
            group_key = (str(flow.tenant_id), vertical_key, scope_key)
            groups[group_key].append(flow)

        changes = 0
        for group_key, flows in groups.items():
            if len(flows) <= 1:
                continue
            flows_sorted = sorted(flows, key=_winner_key, reverse=True)
            winner = flows_sorted[0]
            losers = flows_sorted[1:]
            tenant_id, vertical_key, scope_key = group_key
            print(
                f"[MULTI] tenant={tenant_id} vertical={vertical_key} scope={scope_key} "
                f"published={len(flows)} -> keep {winner.id} v{winner.version}"
            )
            for flow in losers:
                print(f"  - unpublish {flow.id} v{flow.version}")
                if apply:
                    flow.estado = "draft"
                    flow.published_at = None
                    db.add(flow)
                    changes += 1

        if apply and changes:
            db.commit()
        elif apply:
            db.rollback()
        return changes
    except OperationalError as exc:
        print(f"ERROR: database connection failed ({exc.__class__.__name__})")
        print("Hint: ensure DATABASE_URL is reachable (docker compose db).")
        return 1
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Cleanup multiple published flows per tenant/scope group.")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default: dry-run)")
    args = parser.parse_args()
    changes = cleanup(apply=bool(args.apply))
    if args.apply:
        print(f"Applied changes: {changes}")
    else:
        print("Dry-run complete. Use --apply to enforce changes.")


if __name__ == "__main__":
    main()
