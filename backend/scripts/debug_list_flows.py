from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.exc import OperationalError

from app.db.session import SessionLocal
from app.models.configs import Config
from app.models.flows import Flow
from app.models.tenants import Tenant
from app.services import verticals


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _verticals_dir() -> Path:
    return _repo_root() / "app" / "verticals"


def _scopes_for_vertical(vertical_key: str, cfg: dict) -> list[str]:
    scopes: list[str] = []
    v2_scopes = cfg.get("scopes") if isinstance(cfg.get("scopes"), dict) else None
    if isinstance(v2_scopes, dict):
        scopes.extend([str(k) for k in v2_scopes.keys() if k])
    defs = cfg.get("scope_definitions") if isinstance(cfg.get("scope_definitions"), dict) else None
    if isinstance(defs, dict):
        scopes.extend([str(k) for k in defs.keys() if k])
    scope_cfg = cfg.get("scope") if isinstance(cfg.get("scope"), dict) else {}
    included = scope_cfg.get("included") if isinstance(scope_cfg.get("included"), list) else []
    scopes.extend([str(x) for x in included if x])
    out: list[str] = []
    seen: set[str] = set()
    for s in scopes:
        key = str(s).strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def _scope_assets(vertical_key: str, scope: str) -> dict[str, object]:
    vdir = _verticals_dir() / vertical_key
    legacy_flow = vdir / f"flow_base_scope_{scope}.json"
    legacy_subflows = list(vdir.glob(f"subflow_scope_{scope}__*.json"))
    v2_subflows = list((vdir / "subflows" / scope).rglob("*.json")) if (vdir / "subflows").exists() else []
    return {
        "flow_base_scope": legacy_flow.exists(),
        "legacy_subflows": len(legacy_subflows),
        "v2_subflows": len(v2_subflows),
    }


def _scope_state(assets: dict[str, object]) -> str:
    has_flow = bool(assets.get("flow_base_scope"))
    legacy_count = int(assets.get("legacy_subflows") or 0)
    v2_count = int(assets.get("v2_subflows") or 0)
    if not has_flow and legacy_count == 0 and v2_count == 0:
        return "NO_FLOW_YET"
    if has_flow and legacy_count == 0 and v2_count == 0:
        return "DRAFT_ONLY"
    return "HAS_SUBFLOWS"


def _print_header(title: str) -> None:
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)


def main() -> None:
    print(f"Debug flow visibility report @ {datetime.now(timezone.utc).isoformat()}")
    vitems = verticals.list_verticals()
    vertical_keys = [str(v.get("key")) for v in vitems if v.get("key")]

    _print_header("VERTICAL CATALOG (filesystem-backed)")
    for v in vertical_keys:
        cfg = verticals.get_vertical_config(v)
        scopes = _scopes_for_vertical(v, cfg)
        print(f"- {v} | scopes={len(scopes)}")
        for scope in scopes:
            assets = _scope_assets(v, scope)
            state = _scope_state(assets)
            print(
                f"  • {scope}: state={state} flow_base_scope={assets['flow_base_scope']} "
                f"legacy_subflows={assets['legacy_subflows']} v2_subflows={assets['v2_subflows']}"
            )

    _print_header("DB FLOWS (per tenant)")
    db = SessionLocal()
    try:
        tenants = db.query(Tenant).all()
        flows = db.query(Flow).all()
        flows_by_tenant: dict[str, list[Flow]] = defaultdict(list)
        for f in flows:
            flows_by_tenant[str(f.tenant_id)].append(f)

        for t in tenants:
            tid = str(t.id)
            tflows = flows_by_tenant.get(tid, [])
            published = [f for f in tflows if str(f.estado or "").lower() == "published"]
            drafts = [f for f in tflows if str(f.estado or "").lower() != "published"]
            scopes = []
            branding = getattr(t, "branding", {}) or {}
            raw_scopes = branding.get("vertical_scopes") or []
            if isinstance(raw_scopes, list):
                scopes = [str(s) for s in raw_scopes if s]
            latest_pub = sorted(
                published,
                key=lambda x: (
                    x.published_at or datetime.min.replace(tzinfo=timezone.utc),
                    x.version or 0,
                ),
                reverse=True,
            )
            latest_pub_id = str(latest_pub[0].id) if latest_pub else None
            latest_pub_ver = latest_pub[0].version if latest_pub else None
            print(
                f"- tenant={tid} vertical={t.vertical_key or '—'} scopes={scopes or []} "
                f"flows_total={len(tflows)} published={len(published)} drafts={len(drafts)} "
                f"latest_published={latest_pub_id or '—'} v{latest_pub_ver or '—'}"
            )
            if len(published) > 1:
                print("  ! MULTIPLE_PUBLISHED")

        _print_header("INCONSISTENCIES")
        orphan_flows = [f for f in flows if not f.tenant_id]
        if orphan_flows:
            print(f"- flows without tenant_id: {len(orphan_flows)}")
        else:
            print("- flows without tenant_id: 0")
        tenants_missing_vertical = [t for t in tenants if not getattr(t, "vertical_key", None)]
        print(f"- tenants missing vertical_key: {len(tenants_missing_vertical)}")

        _print_header("CONFIG OVERRIDES (tenant configs)")
        configs = db.query(Config).all()
        by_type: dict[str, int] = defaultdict(int)
        for c in configs:
            by_type[str(c.tipo or "unknown")] += 1
        for k in sorted(by_type.keys()):
            print(f"- {k}: {by_type[k]}")
    except OperationalError as exc:
        print(f"- ERROR: database connection failed ({exc.__class__.__name__})")
        print("  Hint: ensure DATABASE_URL is reachable (e.g. docker compose db).")
    finally:
        db.close()


if __name__ == "__main__":
    main()
