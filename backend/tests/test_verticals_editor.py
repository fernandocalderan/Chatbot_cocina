from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from admin_panel.verticals_schema import normalize_problem, unique_slug


def _read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, dict) else {}


def _parse_subflow_filename(name: str) -> tuple[str, str, str] | None:
    if not name.startswith("subflow_scope_") or not name.endswith(".json"):
        return None
    rest = name.removeprefix("subflow_scope_").removesuffix(".json")
    parts = rest.split("__")
    if len(parts) != 3:
        return None
    return parts[0], parts[1], parts[2]


def test_verticals_editor_schema_loads():
    verticals = ["home_services", "kitchens", "clinics_private"]
    base_dir = ROOT / "backend" / "app" / "verticals"
    for key in verticals:
        vdir = base_dir / key
        meta = _read_json(vdir / "metadata.json")
        assert meta.get("vertical_key") == key
        scope_defs = meta.get("scope_definitions")
        assert isinstance(scope_defs, dict)
        for sk, sdef in scope_defs.items():
            assert isinstance(sdef, dict)
            assert "flow_id" in sdef
            assert "problem_groups" in sdef
            assert isinstance(sdef.get("problem_groups"), list)

        flow = _read_json(vdir / "flow_base.json")
        assert isinstance(flow.get("blocks"), dict)

        for sf_path in vdir.glob("subflow_scope_*__*__*.json"):
            parsed = _parse_subflow_filename(sf_path.name)
            assert parsed is not None
            scope, save_to, key_part = parsed
            data = _read_json(sf_path)
            cfg = data.get("config") if isinstance(data.get("config"), dict) else {}
            raw_problem = cfg.get("problem") if isinstance(cfg.get("problem"), dict) else {}
            label = ""
            sub = cfg.get("subflow") if isinstance(cfg.get("subflow"), dict) else {}
            if sub.get("label"):
                label = str(sub.get("label"))
            normalized = normalize_problem(raw_problem, default_group=save_to, title=label or key_part)
            assert isinstance(normalized.get("symptoms"), list)
            assert isinstance(normalized.get("key_questions"), list)
            assert isinstance(normalized.get("fields_to_capture"), list)


def test_unique_slug_generation():
    existing = {"kitchens", "kitchens_2"}
    assert unique_slug("kitchens", existing) == "kitchens_3"
