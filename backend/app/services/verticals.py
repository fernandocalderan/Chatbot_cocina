from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import app.db.session as db_session
from app.models.configs import Config
from app.models.tenants import Tenant


_VERTICALS_DIR = Path(__file__).resolve().parent.parent / "verticals"
_REGISTRY_PATH = _VERTICALS_DIR / "registry.json"
_DEFAULT_VERTICAL_KEY = os.getenv("DEFAULT_VERTICAL_KEY") or "kitchens"

_VERTICAL_PROMPT_FILENAME = "prompt_vertical.txt"
_VERTICAL_PROMPT_EXTENSION_FILENAME = "prompt_vertical_extension.txt"
_VERTICAL_SCOPE_PROMPT_PREFIX = "prompt_scope_"
_VERTICAL_METADATA_FILENAME = "metadata.json"
_VERTICAL_SEMANTIC_SCHEMA_FILENAME = "semantic_schema.json"
_VERTICAL_KPI_DEFAULTS_FILENAME = "kpi_defaults.json"
_VERTICAL_FLOW_BASE_FILENAME = "flow_base.json"
_VERTICAL_FLOW_BASE_SCOPE_PREFIX = "flow_base_scope_"
_VERTICAL_SUBFLOW_PREFIX = "subflow_scope_"
_VERTICAL_ROUTER_ROUTES_PREFIX = "router_routes_scope_"

CONFIG_TIPO_SEMANTIC_SCHEMA = "tenant_semantic_schema"
CONFIG_TIPO_KPI_DEFAULTS = "tenant_kpi_defaults"
CONFIG_TIPO_AI_CONFIG = "tenant_ai_config"
TENANT_BRANDING_SCOPES_KEY = "vertical_scopes"
TENANT_BRANDING_CUSTOM_FLOW_ENABLED_KEY = "custom_flow_enabled"


def _vertical_dir(vertical_key: str) -> Path:
    return _VERTICALS_DIR / str(vertical_key).strip()


def _read_text(path: Path) -> str | None:
    try:
        if not path.exists():
            return None
        text = path.read_text(encoding="utf-8")
        text = text.strip()
        return text or None
    except Exception:
        return None


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        if not path.exists():
            return None
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _load_registry() -> dict[str, Any]:
    if _REGISTRY_PATH.exists():
        with _REGISTRY_PATH.open() as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    return {}


def _scan_vertical_dirs() -> dict[str, dict[str, Any]]:
    items: dict[str, dict[str, Any]] = {}
    try:
        for child in sorted(_VERTICALS_DIR.iterdir()):
            if not child.is_dir():
                continue
            key = child.name.strip()
            if not key or key.startswith(".") or key.startswith("__"):
                continue
            meta = _read_json(child / _VERTICAL_METADATA_FILENAME)
            if not meta:
                continue
            vkey = str(meta.get("vertical_key") or key).strip()
            if not vkey:
                continue
            items[vkey] = meta
    except Exception:
        return items
    return items


def _registry_keys() -> list[str]:
    registry = _load_registry()
    keys = set([str(k) for k in registry.keys()]) if isinstance(registry, dict) else set()
    keys.update(_scan_vertical_dirs().keys())
    return sorted([k for k in keys if k])


def list_verticals() -> list[dict[str, Any]]:
    items = []
    for key in _registry_keys():
        cfg = get_vertical_config(key)
        label = cfg.get("label") or key.replace("_", " ").title()
        defs = vertical_scope_definitions(key)
        scope_cfg = cfg.get("scope") if isinstance(cfg.get("scope"), dict) else {}
        included = scope_cfg.get("included") if isinstance(scope_cfg.get("included"), list) else []
        scope_items = []
        for s in [str(x) for x in included if x]:
            entry = defs.get(s) if isinstance(defs, dict) else None
            scope_items.append({"key": s, "label": (entry.get("label") if isinstance(entry, dict) else None) or s})
        vdir = _vertical_dir(key)
        files = {
            "metadata.json": (vdir / _VERTICAL_METADATA_FILENAME).exists(),
            "flow_base.json": (vdir / _VERTICAL_FLOW_BASE_FILENAME).exists(),
            "prompt_vertical.txt": (vdir / _VERTICAL_PROMPT_FILENAME).exists(),
            "prompt_vertical_extension.txt": (vdir / _VERTICAL_PROMPT_EXTENSION_FILENAME).exists(),
            "semantic_schema.json": (vdir / _VERTICAL_SEMANTIC_SCHEMA_FILENAME).exists(),
            "kpi_defaults.json": (vdir / _VERTICAL_KPI_DEFAULTS_FILENAME).exists(),
        }
        flow_template_exists = bool(files.get("flow_base.json"))
        flow_source = "verticals" if flow_template_exists else "none"
        items.append(
            {
                "key": key,
                "label": label,
                "default_flow_id": cfg.get("default_flow_id"),
                "flow_ids": cfg.get("flow_ids") if isinstance(cfg.get("flow_ids"), list) else None,
                "promise_commercial": cfg.get("promise_commercial"),
                "scope": cfg.get("scope") if isinstance(cfg.get("scope"), dict) else None,
                "scope_items": scope_items or None,
                "locks": cfg.get("locks") if isinstance(cfg.get("locks"), dict) else None,
                "conversational_intelligence": cfg.get("conversational_intelligence")
                if isinstance(cfg.get("conversational_intelligence"), dict)
                else None,
                "assets": cfg.get("assets") if isinstance(cfg.get("assets"), dict) else None,
                "files": files,
                "flow_template_exists": flow_template_exists,
                "flow_source": flow_source,
            }
        )
    return items


def get_vertical_bundle(vertical_key: str | None) -> dict[str, Any]:
    """
    Devuelve el vertical con sus assets (solo lectura) para el panel ADMIN.
    No depende de que el vertical esté provisionado en tenants.
    """
    if not vertical_key:
        return {}
    cfg = get_vertical_config(vertical_key)
    if not cfg:
        return {}
    key = str(cfg.get("vertical_key") or vertical_key).strip()
    vdir = _vertical_dir(key)
    files = {
        "metadata.json": (vdir / _VERTICAL_METADATA_FILENAME).exists(),
        "flow_base.json": (vdir / _VERTICAL_FLOW_BASE_FILENAME).exists(),
        "prompt_vertical.txt": (vdir / _VERTICAL_PROMPT_FILENAME).exists(),
        "prompt_vertical_extension.txt": (vdir / _VERTICAL_PROMPT_EXTENSION_FILENAME).exists(),
        "semantic_schema.json": (vdir / _VERTICAL_SEMANTIC_SCHEMA_FILENAME).exists(),
        "kpi_defaults.json": (vdir / _VERTICAL_KPI_DEFAULTS_FILENAME).exists(),
    }
    return {
        "key": key,
        "config": cfg,
        "files": files,
        "assets": {
            "metadata": _read_json(vdir / _VERTICAL_METADATA_FILENAME),
            "flow_base": vertical_flow_base(key),
            "semantic_schema": vertical_semantic_schema(key),
            "kpi_defaults": vertical_kpi_defaults(key),
            "prompt_vertical": _read_text(vdir / _VERTICAL_PROMPT_FILENAME),
            "prompt_vertical_extension": _read_text(vdir / _VERTICAL_PROMPT_EXTENSION_FILENAME),
        },
    }


def get_vertical_config(vertical_key: str | None) -> dict[str, Any]:
    if not vertical_key:
        return {}
    registry = _load_registry()
    cfg = registry.get(vertical_key, {}) if isinstance(registry, dict) else {}
    meta = _read_json(_vertical_dir(str(vertical_key)) / _VERTICAL_METADATA_FILENAME) or {}
    if not meta:
        return cfg if isinstance(cfg, dict) else {}
    merged = dict(cfg) if isinstance(cfg, dict) else {}
    merged.update(meta)
    return merged


def _normalize_scopes(raw: object) -> list[str]:
    if not raw:
        return []
    scopes: list[str] = []
    if isinstance(raw, str):
        scopes = [raw]
    elif isinstance(raw, list):
        scopes = [str(s) for s in raw if s]
    elif isinstance(raw, tuple):
        scopes = [str(s) for s in raw if s]
    else:
        return []
    out: list[str] = []
    seen: set[str] = set()
    for s in scopes:
        key = str(s).strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def vertical_scope_definitions(vertical_key: str | None) -> dict[str, Any]:
    cfg = get_vertical_config(vertical_key)
    defs = cfg.get("scope_definitions") if isinstance(cfg, dict) else None
    return defs if isinstance(defs, dict) else {}


def vertical_subflows_config(vertical_key: str | None) -> dict[str, Any]:
    cfg = get_vertical_config(vertical_key)
    sub = cfg.get("subflows") if isinstance(cfg, dict) else None
    return sub if isinstance(sub, dict) else {}


def vertical_subflow_locks(vertical_key: str | None) -> dict[str, Any]:
    sub = vertical_subflows_config(vertical_key)
    locks = sub.get("locks") if isinstance(sub.get("locks"), dict) else {}
    return locks if isinstance(locks, dict) else {}


def vertical_subflow_recommended_order(vertical_key: str | None) -> list[str]:
    sub = vertical_subflows_config(vertical_key)
    order = sub.get("recommended_order")
    if isinstance(order, list):
        return [str(x) for x in order if x]
    return []


def vertical_subflow_composition_default(vertical_key: str | None) -> str:
    sub = vertical_subflows_config(vertical_key)
    return str(sub.get("composition_default") or "router").strip().lower()


def allowed_scopes(vertical_key: str | None) -> list[str]:
    cfg = get_vertical_config(vertical_key)
    scope_cfg = cfg.get("scope") if isinstance(cfg, dict) else None
    included = scope_cfg.get("included") if isinstance(scope_cfg, dict) else None
    if isinstance(included, list) and included:
        return [str(s) for s in included if s]
    return sorted([k for k in vertical_scope_definitions(vertical_key).keys() if k])


def validate_vertical_scopes(vertical_key: str | None, scopes: object) -> list[str]:
    normalized = _normalize_scopes(scopes)
    allowed = set(allowed_scopes(vertical_key))
    if not allowed:
        return [] if not normalized else normalized
    invalid = [s for s in normalized if s not in allowed]
    if invalid:
        raise ValueError(f"invalid_vertical_scopes: {', '.join(invalid)}")
    return normalized


def tenant_vertical_scopes(tenant: Tenant | None) -> list[str]:
    if not tenant:
        return []
    branding = getattr(tenant, "branding", {}) or {}
    return _normalize_scopes(branding.get(TENANT_BRANDING_SCOPES_KEY))


def tenant_custom_flow_enabled(tenant: Tenant | None) -> bool:
    """
    Cuando es False, el runtime ignora flows publicados en DB y usa el flujo base (vertical + scope).
    Se guarda en `tenants.branding.custom_flow_enabled` (sin migración).
    """
    if not tenant:
        return False
    branding = getattr(tenant, "branding", {}) or {}
    return bool(branding.get(TENANT_BRANDING_CUSTOM_FLOW_ENABLED_KEY) or False)


def scope_defaults(vertical_key: str | None, scopes: object) -> dict[str, Any]:
    normalized = _normalize_scopes(scopes)
    if len(normalized) != 1:
        return {}
    entry = vertical_scope_definitions(vertical_key).get(normalized[0])
    defaults = entry.get("defaults") if isinstance(entry, dict) else None
    return defaults if isinstance(defaults, dict) else {}


def vertical_scope_prompt(vertical_key: str | None, scope_key: str | None) -> str | None:
    if not vertical_key or not scope_key:
        return None
    sk = str(scope_key).strip().lower()
    if not sk:
        return None
    vdir = _vertical_dir(str(vertical_key).strip())
    return _read_text(vdir / f"{_VERTICAL_SCOPE_PROMPT_PREFIX}{sk}.txt")


def vertical_scope_prompts(vertical_key: str | None, scopes: object) -> list[str]:
    out: list[str] = []
    for s in _normalize_scopes(scopes):
        txt = vertical_scope_prompt(vertical_key, s)
        if txt:
            out.append(txt)
    return out


def _deep_merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(merged.get(k), dict):
            merged[k] = _deep_merge_dicts(merged[k], v)  # type: ignore[arg-type]
        else:
            merged[k] = v
    return merged


def allowed_flow_ids(vertical_key: str | None) -> list[str]:
    effective_key = vertical_key or _DEFAULT_VERTICAL_KEY
    cfg = get_vertical_config(effective_key)
    flow_ids = cfg.get("flow_ids")
    if isinstance(flow_ids, list) and flow_ids:
        return [str(f) for f in flow_ids]
    default_flow = cfg.get("default_flow_id")
    return [str(default_flow)] if default_flow else []


def default_flow_id(vertical_key: str | None) -> str | None:
    effective_key = vertical_key or _DEFAULT_VERTICAL_KEY
    cfg = get_vertical_config(effective_key)
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
    # Para verticals, los templates provienen de `app/verticals/<key>/flow_base.json`.
    # `app/flows/*.json` queda como legacy/migración y no se usa en runtime.
    effective_key = vertical_key or _DEFAULT_VERTICAL_KEY
    cfg = get_vertical_config(effective_key)
    flow_id = cfg.get("default_flow_id")
    if flow_id and (_vertical_dir(str(effective_key)) / _VERTICAL_FLOW_BASE_FILENAME).exists():
        label = cfg.get("label") or str(effective_key).replace("_", " ").title()
        return [{"id": str(flow_id), "label": f"{label} (Base)"}]
    return []


def vertical_prompt(vertical_key: str | None) -> str | None:
    if not vertical_key:
        return None
    prompt_from_file = _read_text(_vertical_dir(str(vertical_key)) / _VERTICAL_PROMPT_FILENAME)
    if prompt_from_file:
        return prompt_from_file
    cfg = get_vertical_config(vertical_key)
    prompt = cfg.get("vertical_prompt")
    return str(prompt).strip() if prompt else None


def vertical_prompt_extension(vertical_key: str | None) -> str | None:
    if not vertical_key:
        return None
    return _read_text(_vertical_dir(str(vertical_key)) / _VERTICAL_PROMPT_EXTENSION_FILENAME)


def vertical_semantic_schema(vertical_key: str | None) -> dict[str, Any] | None:
    if not vertical_key:
        return None
    return _read_json(_vertical_dir(str(vertical_key)) / _VERTICAL_SEMANTIC_SCHEMA_FILENAME)


def vertical_kpi_defaults(vertical_key: str | None) -> dict[str, Any] | None:
    if not vertical_key:
        return None
    return _read_json(_vertical_dir(str(vertical_key)) / _VERTICAL_KPI_DEFAULTS_FILENAME)

def vertical_flow_base(vertical_key: str | None, scopes: object = None) -> dict[str, Any] | None:
    if not vertical_key:
        return None
    vdir = _vertical_dir(str(vertical_key))
    base = _read_json(vdir / _VERTICAL_FLOW_BASE_FILENAME)
    if not isinstance(base, dict):
        return None
    chosen = _normalize_scopes(scopes)
    if not chosen:
        return base
    # La estructura del flow se define por el scope "principal".
    # Si hay varios scopes, el primero es el principal (los demás influyen en prompts/KB).
    scope_key = chosen[0]
    # Canonical: flow_base_scope_<scope>.json (compat: flow_scope_<scope>.json)
    scope_path = vdir / f"{_VERTICAL_FLOW_BASE_SCOPE_PREFIX}{scope_key}.json"
    legacy_scope_path = vdir / f"flow_scope_{scope_key}.json"
    for p in (scope_path, legacy_scope_path):
        if p.exists():
            scoped = _read_json(p)
            if isinstance(scoped, dict):
                return scoped
    entry = vertical_scope_definitions(vertical_key).get(scope_key)
    if not isinstance(entry, dict):
        return base
    overrides = entry.get("flow_overrides")
    if isinstance(overrides, dict) and overrides:
        return _deep_merge_dicts(base, overrides)
    return base


def vertical_read_asset_json(vertical_key: str | None, filename: str) -> dict[str, Any] | None:
    """
    Lee un JSON adicional del vertical (p.ej. router_routes_scope_* o subflow_scope_*).
    Se limita a nombres de archivo simples (sin subdirectorios) para evitar path traversal.
    """
    if not vertical_key:
        return None
    name = str(filename or "").strip()
    if not name or "/" in name or "\\" in name:
        return None
    vdir = _vertical_dir(str(vertical_key))
    path = vdir / name
    data = _read_json(path)
    return data if isinstance(data, dict) else None


def parse_vertical_subflow_filename(filename: str) -> dict[str, str] | None:
    """
    Soporta: subflow_scope_<scope>__<save_to>__<key>.json
    """
    name = str(filename or "").strip()
    if not name.startswith(_VERTICAL_SUBFLOW_PREFIX) or not name.endswith(".json"):
        return None
    rest = name.removeprefix(_VERTICAL_SUBFLOW_PREFIX).removesuffix(".json")
    parts = rest.split("__")
    if len(parts) != 3:
        return None
    scope_key, save_to, key = [str(p or "").strip().lower() for p in parts]
    if not scope_key or not save_to or not key:
        return None
    if "/" in scope_key or "\\" in scope_key or "/" in save_to or "\\" in save_to or "/" in key or "\\" in key:
        return None
    return {"scope": scope_key, "save_to": save_to, "key": key}


def build_vertical_subflow_filename(*, scope: str, save_to: str, key: str) -> str:
    scope_norm = str(scope or "").strip().lower()
    save_to_norm = str(save_to or "").strip().lower()
    key_norm = str(key or "").strip().lower()
    return f"{_VERTICAL_SUBFLOW_PREFIX}{scope_norm}__{save_to_norm}__{key_norm}.json"


def parse_vertical_router_routes_filename(filename: str) -> dict[str, str] | None:
    """
    Soporta: router_routes_scope_<scope>__<save_to>.json
    """
    name = str(filename or "").strip()
    if not name.startswith(_VERTICAL_ROUTER_ROUTES_PREFIX) or not name.endswith(".json"):
        return None
    rest = name.removeprefix(_VERTICAL_ROUTER_ROUTES_PREFIX).removesuffix(".json")
    if "__" not in rest:
        return None
    scope_key, save_to = [str(p or "").strip().lower() for p in rest.split("__", 1)]
    if not scope_key or not save_to:
        return None
    if "/" in scope_key or "\\" in scope_key or "/" in save_to or "\\" in save_to:
        return None
    return {"scope": scope_key, "save_to": save_to}


def vertical_list_subflows(
    vertical_key: str | None,
    *,
    scope: str | None = None,
    save_to: str | None = None,
) -> list[dict[str, str]]:
    """
    Lista subflows existentes como colección abierta del scope.
    Devuelve items: {"filename","scope","save_to","key"}.
    """
    if not vertical_key:
        return []
    vdir = _vertical_dir(str(vertical_key))
    if not vdir.exists():
        return []
    scope_norm = str(scope or "").strip().lower() or None
    save_to_norm = str(save_to or "").strip().lower() or None
    items: list[dict[str, str]] = []
    try:
        for path in sorted(vdir.glob(f"{_VERTICAL_SUBFLOW_PREFIX}*.json")):
            meta = parse_vertical_subflow_filename(path.name)
            if not meta:
                continue
            if scope_norm and meta["scope"] != scope_norm:
                continue
            if save_to_norm and meta["save_to"] != save_to_norm:
                continue
            items.append({"filename": path.name, **meta})
    except Exception:
        return items
    return items


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
            "ai_level": "low",
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


def provision_vertical_assets(db, tenant: Tenant) -> dict[str, Any] | None:
    """
    Provisioning idempotente (solo creación inicial) de assets de vertical.
    - NO sobrescribe assets si ya existen.
    - No cambia el runtime del widget (solo crea configs/flows).
    """
    if not tenant or not tenant.vertical_key:
        return None

    created: dict[str, Any] = {"created": [], "vertical_key": str(tenant.vertical_key)}

    # 1) Mantener compatibilidad: siempre provisionar materiales si faltan.
    try:
        materials = provision_vertical_materials(db, tenant)
        if materials is not None:
            created["materials"] = True
    except Exception:
        pass

    # 2) Esquema semántico base (config semántica)
    if not (
        db.query(Config)
        .filter(Config.tenant_id == tenant.id, Config.tipo == CONFIG_TIPO_SEMANTIC_SCHEMA)
        .order_by(Config.version.desc())
        .first()
    ):
        schema = vertical_semantic_schema(tenant.vertical_key)
        if schema:
            db.add(
                Config(
                    tenant_id=tenant.id,
                    tipo=CONFIG_TIPO_SEMANTIC_SCHEMA,
                    version=1,
                    payload_json=schema,
                )
            )
            created["created"].append(CONFIG_TIPO_SEMANTIC_SCHEMA)

    # 3) KPI defaults
    if not (
        db.query(Config)
        .filter(Config.tenant_id == tenant.id, Config.tipo == CONFIG_TIPO_KPI_DEFAULTS)
        .order_by(Config.version.desc())
        .first()
    ):
        kpis = vertical_kpi_defaults(tenant.vertical_key)
        if kpis:
            db.add(
                Config(
                    tenant_id=tenant.id,
                    tipo=CONFIG_TIPO_KPI_DEFAULTS,
                    version=1,
                    payload_json=kpis,
                )
            )
            created["created"].append(CONFIG_TIPO_KPI_DEFAULTS)

    # 4) Prompt de vertical (config IA del tenant, bloqueado)
    if not (
        db.query(Config)
        .filter(Config.tenant_id == tenant.id, Config.tipo == CONFIG_TIPO_AI_CONFIG)
        .order_by(Config.version.desc())
        .first()
    ):
        v_prompt = vertical_prompt(tenant.vertical_key)
        if v_prompt:
            db.add(
                Config(
                    tenant_id=tenant.id,
                    tipo=CONFIG_TIPO_AI_CONFIG,
                    version=1,
                    payload_json={
                        "vertical_prompt": v_prompt,
                        "locked": {"vertical_prompt": True},
                    },
                )
            )
            created["created"].append(CONFIG_TIPO_AI_CONFIG)

    # 5) Flow base (clonado en tabla flows si está disponible)
    try:
        from datetime import datetime, timezone

        from app.models.flows import Flow as FlowVersioned

        existing_flow = (
            db.query(FlowVersioned)
            .filter(FlowVersioned.tenant_id == tenant.id, FlowVersioned.estado == "published")
            .order_by(FlowVersioned.version.desc())
            .first()
        )
        if not existing_flow:
            flow = vertical_flow_base(tenant.vertical_key, tenant_vertical_scopes(tenant))
            if flow:
                new_flow = FlowVersioned(
                    tenant_id=tenant.id,
                    vertical_key=str(tenant.vertical_key) if tenant.vertical_key else None,
                    version=1,
                    schema_json=flow,
                    estado="published",
                    published_at=datetime.now(timezone.utc),
                )
                db.add(new_flow)
                # Asociar flow activo (si el modelo lo soporta)
                try:
                    tenant.active_flow_id = new_flow.id
                    tenant.flow_mode = "VERTICAL"
                    db.add(tenant)
                except Exception:
                    pass
                created["created"].append("flows:published_v1")
            else:
                new_flow = None
        else:
            # Mantener active_flow_id apuntando al publicado actual si aún no está seteado.
            try:
                if not getattr(tenant, "active_flow_id", None):
                    tenant.active_flow_id = existing_flow.id
                    tenant.flow_mode = "VERTICAL"
                    db.add(tenant)
            except Exception:
                pass
            new_flow = existing_flow
    except Exception:
        # La tabla puede no estar migrada / disponible en ciertos entornos.
        pass

    try:
        db.commit()
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass

    return created


def fetch_tenant_vertical_key(tenant_id: str | None) -> str | None:
    if not tenant_id:
        return None
    session = db_session.SessionLocal()
    try:
        tenant = session.query(Tenant).filter(Tenant.id == tenant_id).first()
        return str(tenant.vertical_key) if tenant and tenant.vertical_key else None
    finally:
        session.close()
