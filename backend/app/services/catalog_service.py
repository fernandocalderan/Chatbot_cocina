from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.models.flows import Flow
from app.models.tenants import Tenant
from app.schemas.catalog import CatalogFlow, CatalogScope, CatalogVertical, CatalogWarning, CatalogResponse
from app.services import verticals


_VERTICALS_DIR = Path(__file__).resolve().parent.parent / "verticals"


def _normalize_scopes(raw: object) -> list[str]:
    if not raw:
        return []
    if isinstance(raw, list):
        items = [str(s).strip() for s in raw if s]
    elif isinstance(raw, tuple):
        items = [str(s).strip() for s in raw if s]
    elif isinstance(raw, str):
        items = [raw.strip()]
    else:
        return []
    out: list[str] = []
    seen: set[str] = set()
    for s in items:
        if not s or s in seen:
            continue
        seen.add(s)
        out.append(s)
    return out


def _scopes_for_vertical(vertical_key: str, cfg: dict[str, Any]) -> list[str]:
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
    return _normalize_scopes(scopes)


def _filesystem_assets(vertical_key: str, scope_key: str) -> dict[str, int | bool]:
    vdir = _VERTICALS_DIR / vertical_key
    legacy_flow = vdir / f"flow_base_scope_{scope_key}.json"
    legacy_subflows = list(vdir.glob(f"subflow_scope_{scope_key}__*.json"))
    v2_subflows = list((vdir / "subflows" / scope_key).rglob("*.json")) if (vdir / "subflows").exists() else []
    return {
        "flow_base_scope": legacy_flow.exists(),
        "legacy_subflows": len(legacy_subflows),
        "v2_subflows": len(v2_subflows),
    }


def _scope_has_filesystem_definition(assets: dict[str, int | bool]) -> bool:
    return bool(assets.get("flow_base_scope")) or int(assets.get("legacy_subflows") or 0) > 0 or int(
        assets.get("v2_subflows") or 0
    ) > 0


def _catalog_status(flows: list[CatalogFlow]) -> str:
    published_count = len([f for f in flows if f.published])
    if published_count > 1:
        return "MULTIPLE_PUBLISHED"
    if published_count == 1:
        return "PUBLISHED_OK"
    if flows:
        return "DRAFT_ONLY"
    return "NO_FLOW_YET"


def list_catalog(
    db: Session,
    *,
    vertical_key: str | None = None,
    tenant_id: str | None = None,
    include_empty_scopes: bool = True,
    include_drafts: bool = True,
    include_templates: bool = True,
    only_published: bool = False,
) -> CatalogResponse:
    warnings: list[CatalogWarning] = []
    vertical_items = verticals.list_verticals()
    vertical_keys = [str(v.get("key")) for v in vertical_items if v.get("key")]
    if vertical_key:
        vertical_keys = [k for k in vertical_keys if k == vertical_key]

    scopes_by_vertical: dict[str, dict[str, CatalogScope]] = {}
    for vkey in vertical_keys:
        cfg = verticals.get_vertical_config(vkey)
        scopes = _scopes_for_vertical(vkey, cfg)
        scopes_by_vertical.setdefault(vkey, {})
        for scope_key in scopes:
            assets = _filesystem_assets(vkey, scope_key)
            has_fs = _scope_has_filesystem_definition(assets)
            flow_entries: list[CatalogFlow] = []
            if include_templates and assets.get("flow_base_scope"):
                flow_entries.append(
                    CatalogFlow(
                        flow_id=f"fs:flow_base_scope_{scope_key}.json",
                        name=f"flow_base_scope_{scope_key}.json",
                        version=None,
                        published=False,
                        published_at=None,
                        owner_type="GLOBAL",
                        owner_id=None,
                    )
                )
            scopes_by_vertical[vkey][scope_key] = CatalogScope(
                scope_key=scope_key,
                source="FILESYSTEM",
                has_filesystem_definition=has_fs,
                flows=flow_entries,
                status="NO_FLOW_YET",
            )

    q = db.query(Flow).join(Tenant, Flow.tenant_id == Tenant.id)
    if tenant_id:
        q = q.filter(Flow.tenant_id == tenant_id)

    flows = q.all()
    tenant_map: dict[str, Tenant] = {str(t.id): t for t in db.query(Tenant).all()}

    flows_by_scope: dict[tuple[str, str], list[CatalogFlow]] = defaultdict(list)
    db_only_scopes: set[tuple[str, str]] = set()
    for flow in flows:
        tenant = tenant_map.get(str(flow.tenant_id))
        t_vertical = (flow.vertical_key or getattr(tenant, "vertical_key", None) or "").strip() or None
        if vertical_key and t_vertical != vertical_key:
            continue
        if not t_vertical:
            warnings.append(
                CatalogWarning(code="tenant_missing_vertical_key", detail=f"tenant_id={flow.tenant_id}")
            )
            continue

        branding = getattr(tenant, "branding", {}) or {}
        scopes = _normalize_scopes(branding.get("vertical_scopes") or [])
        scope_key = scopes[0] if scopes else "unknown"
        if scope_key == "unknown":
            warnings.append(
                CatalogWarning(code="tenant_missing_scope", detail=f"tenant_id={flow.tenant_id} vertical={t_vertical}")
            )
        if only_published and str(flow.estado or "").lower() != "published":
            continue
        if not include_drafts and str(flow.estado or "").lower() != "published":
            continue

        entry = CatalogFlow(
            flow_id=str(flow.id),
            name=f"tenant_flow_v{flow.version}",
            version=flow.version,
            published=str(flow.estado or "").lower() == "published",
            published_at=flow.published_at.isoformat() if flow.published_at else None,
            owner_type="TENANT",
            owner_id=str(flow.tenant_id),
        )
        flows_by_scope[(t_vertical, scope_key)].append(entry)
        if t_vertical not in scopes_by_vertical or scope_key not in scopes_by_vertical.get(t_vertical, {}):
            db_only_scopes.add((t_vertical, scope_key))

    for (vkey, scope_key), entries in flows_by_scope.items():
        scopes_by_vertical.setdefault(vkey, {})
        scope_entry = scopes_by_vertical[vkey].get(scope_key)
        if not scope_entry:
            warnings.append(
                CatalogWarning(
                    code="scope_missing_in_filesystem",
                    detail=f"vertical={vkey} scope={scope_key} (DB only)",
                )
            )
            scopes_by_vertical[vkey][scope_key] = CatalogScope(
                scope_key=scope_key,
                source="DB_ONLY",
                has_filesystem_definition=False,
                flows=list(entries),
                status="NO_FLOW_YET",
            )
        else:
            scope_entry.flows.extend(entries)

    verticals_out: list[CatalogVertical] = []
    for vkey in sorted(scopes_by_vertical.keys()):
        scope_items = list(scopes_by_vertical[vkey].values())
        for scope_item in scope_items:
            scope_item.status = _catalog_status(scope_item.flows)
            if scope_item.status == "NO_FLOW_YET" and not include_empty_scopes:
                continue
        scope_items = [s for s in scope_items if include_empty_scopes or s.status != "NO_FLOW_YET"]
        scope_items = sorted(scope_items, key=lambda s: s.scope_key)
        verticals_out.append(CatalogVertical(vertical_key=vkey, scopes=scope_items))

    return CatalogResponse(verticals=verticals_out, warnings=warnings)
