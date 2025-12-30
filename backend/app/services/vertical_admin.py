from __future__ import annotations

import json
import re
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


_VERTICALS_DIR = Path(__file__).resolve().parent.parent / "verticals"
_REGISTRY_PATH = _VERTICALS_DIR / "registry.json"

_KEY_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{1,62}$")

_JSON_FILES = {
    "metadata.json",
    "flow_base.json",
    "semantic_schema.json",
    "kpi_defaults.json",
}
_TEXT_FILES = {
    "prompt_vertical.txt",
    "prompt_vertical_extension.txt",
}

_FLOW_SCOPE_PREFIXES = ("flow_scope_", "flow_base_scope_")
_ROUTER_ROUTES_PREFIX = "router_routes_scope_"
_SUBFLOW_PREFIX = "subflow_scope_"


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    errors: list[str]
    warnings: list[str]


def normalize_vertical_key(raw: str) -> str:
    key = str(raw or "").strip().lower()
    if not key or not _KEY_RE.match(key):
        raise ValueError("invalid_vertical_key")
    return key


def _vertical_dir(vertical_key: str) -> Path:
    key = normalize_vertical_key(vertical_key)
    return _VERTICALS_DIR / key


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(path)


def _backup_if_exists(path: Path) -> None:
    if not path.exists():
        return
    ts = time.strftime("%Y%m%d-%H%M%S")
    bak = path.with_name(f"{path.name}.bak.{ts}")
    try:
        shutil.copy2(path, bak)
    except Exception:
        pass


def _load_registry() -> dict[str, Any]:
    if not _REGISTRY_PATH.exists():
        return {}
    try:
        data = json.loads(_REGISTRY_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _write_registry(registry: dict[str, Any]) -> None:
    _atomic_write(_REGISTRY_PATH, json.dumps(registry, ensure_ascii=False, indent=2).encode("utf-8"))


def validate_flow_schema(flow: Any) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(flow, dict):
        return ValidationResult(ok=False, errors=["flow_not_a_dict"], warnings=[])

    blocks = flow.get("blocks")
    if not isinstance(blocks, dict) or not blocks:
        errors.append("missing_blocks")
        return ValidationResult(ok=False, errors=errors, warnings=warnings)

    ids = set(str(k) for k in blocks.keys() if k)
    start = flow.get("start_block")
    if not isinstance(start, str) or not start.strip():
        errors.append("missing_start_block")
    elif start not in ids:
        errors.append(f"start_block_not_found:{start}")

    def _check_next(next_id: Any, ctx: str) -> None:
        if next_id is None:
            return
        if not isinstance(next_id, str) or not next_id.strip():
            return
        if next_id not in ids:
            errors.append(f"missing_block_ref:{ctx}:{next_id}")

    for bid, block in blocks.items():
        if not isinstance(block, dict):
            warnings.append(f"block_not_a_dict:{bid}")
            continue

        _check_next(block.get("next"), f"{bid}.next")

        nm = block.get("next_map")
        if isinstance(nm, dict):
            for k, v in nm.items():
                _check_next(v, f"{bid}.next_map[{k}]")

        branches = block.get("branches")
        if isinstance(branches, dict):
            for k, v in branches.items():
                _check_next(v, f"{bid}.branches[{k}]")

        if block.get("type") == "condition":
            conditions = block.get("conditions")
            if isinstance(conditions, list):
                for idx, cond in enumerate(conditions):
                    if not isinstance(cond, dict):
                        continue
                    _check_next(cond.get("next"), f"{bid}.conditions[{idx}].next")

    return ValidationResult(ok=not errors, errors=errors, warnings=warnings)


def _allowed_filename(filename: str) -> tuple[str, str]:
    """
    Devuelve (normalized_filename, kind) donde kind ∈ {"json","text","flow_scope"}.
    """
    name = str(filename or "").strip()
    if name in _JSON_FILES:
        return name, "json"
    if name in _TEXT_FILES:
        return name, "text"
    if name.startswith("prompt_scope_") and name.endswith(".txt"):
        scope = name.removeprefix("prompt_scope_").removesuffix(".txt")
        scope_norm = str(scope or "").strip().lower()
        if not scope_norm or not _KEY_RE.match(scope_norm):
            raise ValueError("invalid_scope_key")
        return f"prompt_scope_{scope_norm}.txt", "text"
    for prefix in _FLOW_SCOPE_PREFIXES:
        if name.startswith(prefix) and name.endswith(".json"):
            scope = name.removeprefix(prefix).removesuffix(".json")
            scope_norm = str(scope or "").strip().lower()
            if not scope_norm or not _KEY_RE.match(scope_norm):
                raise ValueError("invalid_scope_key")
            # Canonical filename: flow_base_scope_<scope>.json
            return f"flow_base_scope_{scope_norm}.json", "flow_scope"

    # Router routes mapping file (json dict, no flow schema)
    # router_routes_scope_<scope>__<save_to>.json
    if name.startswith(_ROUTER_ROUTES_PREFIX) and name.endswith(".json"):
        rest = name.removeprefix(_ROUTER_ROUTES_PREFIX).removesuffix(".json")
        if "__" not in rest:
            raise ValueError("invalid_router_routes_filename")
        scope_raw, save_to_raw = rest.split("__", 1)
        scope_norm = str(scope_raw or "").strip().lower()
        save_to_norm = str(save_to_raw or "").strip().lower()
        if not scope_norm or not _KEY_RE.match(scope_norm):
            raise ValueError("invalid_scope_key")
        if not save_to_norm or not _KEY_RE.match(save_to_norm):
            raise ValueError("invalid_router_save_to")
        return f"{_ROUTER_ROUTES_PREFIX}{scope_norm}__{save_to_norm}.json", "json"

    # Subflow flow file (flow schema)
    # subflow_scope_<scope>__<save_to>__<key>.json
    if name.startswith(_SUBFLOW_PREFIX) and name.endswith(".json"):
        rest = name.removeprefix(_SUBFLOW_PREFIX).removesuffix(".json")
        parts = rest.split("__")
        if len(parts) != 3:
            raise ValueError("invalid_subflow_filename")
        scope_raw, save_to_raw, key_raw = parts
        scope_norm = str(scope_raw or "").strip().lower()
        save_to_norm = str(save_to_raw or "").strip().lower()
        key_norm = str(key_raw or "").strip().lower()
        if not scope_norm or not _KEY_RE.match(scope_norm):
            raise ValueError("invalid_scope_key")
        if not save_to_norm or not _KEY_RE.match(save_to_norm):
            raise ValueError("invalid_router_save_to")
        if not key_norm or not _KEY_RE.match(key_norm):
            raise ValueError("invalid_subflow_key")
        return f"{_SUBFLOW_PREFIX}{scope_norm}__{save_to_norm}__{key_norm}.json", "flow_subflow"
    raise ValueError("invalid_filename")


def create_vertical(
    *,
    vertical_key: str,
    label: str | None = None,
    default_flow_id: str | None = None,
    initial_flow: dict[str, Any] | None = None,
) -> dict[str, Any]:
    key = normalize_vertical_key(vertical_key)
    vdir = _vertical_dir(key)
    if vdir.exists():
        raise FileExistsError("vertical_exists")
    vdir.mkdir(parents=True, exist_ok=True)

    flow_id = (default_flow_id or f"{key}_base_v1").strip()
    meta = {
        "vertical_key": key,
        "label": (label or key.replace("_", " ").title()).strip(),
        "default_flow_id": flow_id,
        "flow_ids": [flow_id],
        "assets": {
            "flow_base": "flow_base.json",
            "prompt_vertical": "prompt_vertical.txt",
            "semantic_schema": "semantic_schema.json",
            "kpi_defaults": "kpi_defaults.json",
        },
        "locks": {
            "vertical_key_immutable": True,
        },
    }
    _atomic_write(vdir / "metadata.json", json.dumps(meta, ensure_ascii=False, indent=2).encode("utf-8"))

    flow = initial_flow
    if not isinstance(flow, dict):
        flow = {
            "version": flow_id,
            "plan": "base",
            "start_block": "welcome",
            "languages": ["es"],
            "config": {"ia_enabled": True, "ia_generation_level": 0, "pdf_enabled": False},
            "blocks": {
                "welcome": {
                    "id": "welcome",
                    "type": "message",
                    "text": {"es": f"Hola. Vertical `{key}` (pendiente de configurar)."},
                    "next": "end",
                },
                "end": {"id": "end", "type": "message", "text": {"es": "Fin."}, "next": None},
            },
        }
    res = validate_flow_schema(flow)
    if not res.ok:
        raise ValueError(f"invalid_flow_base:{';'.join(res.errors)}")
    _atomic_write(vdir / "flow_base.json", json.dumps(flow, ensure_ascii=False, indent=2).encode("utf-8"))

    # Seed registry.json (best-effort).
    reg = _load_registry()
    reg[key] = {"label": meta["label"], "default_flow_id": flow_id, "flow_ids": [flow_id]}
    _write_registry(reg)

    return {"key": key, "label": meta["label"], "default_flow_id": flow_id}


def update_vertical_file(
    *,
    vertical_key: str,
    filename: str,
    kind: str,
    content: Any,
    validate: bool = True,
) -> dict[str, Any]:
    key = normalize_vertical_key(vertical_key)
    vdir = _vertical_dir(key)
    if not vdir.exists():
        raise FileNotFoundError("vertical_not_found")
    normalized_name, allowed_kind = _allowed_filename(filename)
    if kind != allowed_kind and not (
        (allowed_kind in {"flow_scope", "flow_subflow"} and kind == "json")
    ):
        raise ValueError("invalid_kind_for_filename")
    path = vdir / normalized_name

    if allowed_kind in {"json", "flow_scope", "flow_subflow"}:
        if not isinstance(content, dict):
            raise ValueError("invalid_json_payload")
        if validate and (
            normalized_name in {"flow_base.json"}
            or normalized_name.startswith(_FLOW_SCOPE_PREFIXES)
            or normalized_name.startswith(_SUBFLOW_PREFIX)
        ):
            res = validate_flow_schema(content)
            if not res.ok:
                raise ValueError(f"invalid_flow:{';'.join(res.errors)}")
        if normalized_name == "metadata.json":
            vkey = str(content.get("vertical_key") or "").strip().lower()
            if vkey and vkey != key:
                raise ValueError("vertical_key_immutable")
            content["vertical_key"] = key

        _backup_if_exists(path)
        _atomic_write(path, json.dumps(content, ensure_ascii=False, indent=2).encode("utf-8"))
        if normalized_name == "metadata.json":
            try:
                reg = _load_registry()
                reg.setdefault(key, {})
                entry = reg[key] if isinstance(reg.get(key), dict) else {}
                for k in ("label", "default_flow_id", "flow_ids"):
                    if k in content:
                        entry[k] = content.get(k)
                reg[key] = entry
                _write_registry(reg)
            except Exception:
                pass
        return {"filename": normalized_name, "kind": allowed_kind}

    if allowed_kind == "text":
        if not isinstance(content, str):
            raise ValueError("invalid_text_payload")
        _backup_if_exists(path)
        _atomic_write(path, (content.strip() + "\n").encode("utf-8"))
        return {"filename": normalized_name, "kind": allowed_kind}

    raise ValueError("invalid_filename")


def read_vertical_file(*, vertical_key: str, filename: str) -> dict[str, Any]:
    key = normalize_vertical_key(vertical_key)
    vdir = _vertical_dir(key)
    if not vdir.exists():
        raise FileNotFoundError("vertical_not_found")
    normalized_name, allowed_kind = _allowed_filename(filename)
    path = vdir / normalized_name
    if not path.exists():
        raise FileNotFoundError("file_not_found")
    if allowed_kind in {"json", "flow_scope"}:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        return {"filename": normalized_name, "kind": "json", "content": data if isinstance(data, dict) else {}}
    if allowed_kind == "text":
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            text = ""
        return {"filename": normalized_name, "kind": "text", "content": text}
    raise ValueError("invalid_filename")
