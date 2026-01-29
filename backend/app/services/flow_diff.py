from __future__ import annotations

from typing import Any


DiffResult = dict[str, list[str]]


def diff_json(base: Any, override: Any, *, max_items: int = 200) -> DiffResult:
    result: DiffResult = {"added": [], "removed": [], "changed": []}

    def _add(bucket: str, path: str) -> None:
        if len(result[bucket]) < max_items:
            result[bucket].append(path or "$")

    def _walk(a: Any, b: Any, path: str) -> None:
        if isinstance(a, dict) and isinstance(b, dict):
            keys = set(a.keys()) | set(b.keys())
            for k in sorted(keys):
                p = f"{path}.{k}" if path else str(k)
                if k not in a:
                    _add("added", p)
                elif k not in b:
                    _add("removed", p)
                else:
                    _walk(a.get(k), b.get(k), p)
            return
        if isinstance(a, list) and isinstance(b, list):
            if len(a) != len(b):
                _add("changed", path)
                return
            for idx, (av, bv) in enumerate(zip(a, b)):
                p = f"{path}[{idx}]" if path else f"[{idx}]"
                _walk(av, bv, p)
            return
        if a != b:
            _add("changed", path)

    _walk(base, override, "")
    return result
