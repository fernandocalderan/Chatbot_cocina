#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests


def _headers(token: str | None, api_key: str | None) -> dict[str, str]:
    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if api_key:
        headers["x-api-key"] = api_key
    return headers


def _resolve_api_key() -> str | None:
    if os.getenv("ADMIN_API_KEY") or os.getenv("ADMIN_API_TOKEN"):
        return os.getenv("ADMIN_API_KEY") or os.getenv("ADMIN_API_TOKEN")
    # Try backend/.env (same logic as admin_panel/api_client)
    here = Path(__file__).resolve()
    env_path = here.parents[1] / "backend" / ".env"
    if not env_path.exists():
        return None
    try:
        for raw in env_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("ADMIN_API_KEY=") or line.startswith("ADMIN_API_TOKEN="):
                return line.split("=", 1)[1].strip()
    except Exception:
        return None
    return None


def _request_json(url: str, *, headers: dict[str, str]) -> dict[str, Any]:
    resp = requests.get(url, headers=headers, timeout=15)
    if not resp.ok:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text}")
    data = resp.json()
    if not isinstance(data, dict):
        raise RuntimeError("invalid_json_response")
    return data


def _infer_vertical_dir(out_dir: Path) -> Path:
    parts = list(out_dir.resolve().parts)
    if "subflows" in parts:
        idx = parts.index("subflows")
        return Path(*parts[:idx])
    return out_dir.parent


def main() -> int:
    parser = argparse.ArgumentParser(description="Export vertical scope subflows from admin API into filesystem")
    parser.add_argument("--vertical", required=True, help="Vertical key (e.g., clinics_private)")
    parser.add_argument("--scope", required=True, help="Scope key (e.g., fisioterapia)")
    parser.add_argument("--router-save-to", default="intent", dest="save_to", help="Router save_to/group (default: intent)")
    parser.add_argument("--out", default=None, help="Output directory for subflows (default: backend/app/verticals/<vertical>/subflows/<scope>/<save_to>)")
    parser.add_argument("--api-base", default=None, help="API base (default: env API_BASE or http://localhost:8100)")
    parser.add_argument("--token", default=None, help="Bearer token (optional)")
    parser.add_argument("--api-key", default=None, help="Admin API key (optional, falls back to backend/.env)")
    parser.add_argument("--include-flow-base", action="store_true", help="Export flow_base_scope_<scope>.json if available")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    parser.add_argument("--layout", choices=["auto", "v2", "legacy"], default="auto", help="Force layout detection")
    args = parser.parse_args()

    api_base = (args.api_base or os.getenv("API_BASE") or "http://localhost:8100").rstrip("/")
    api_key = args.api_key or _resolve_api_key()
    headers = _headers(args.token, api_key)

    out_dir: Path | None = Path(args.out) if args.out else None

    files_url = f"{api_base}/v1/admin/verticals/{args.vertical}/files"
    files_payload = _request_json(files_url, headers=headers)
    items = files_payload.get("items") if isinstance(files_payload, dict) else []
    if not isinstance(items, list):
        items = []

    matches: list[dict[str, Any]] = []
    v2_count = 0
    for it in items:
        if not isinstance(it, dict):
            continue
        sf = it.get("subflow") if isinstance(it.get("subflow"), dict) else None
        if not isinstance(sf, dict):
            continue
        scope = str(sf.get("scope") or "").strip().lower()
        save_to = str(sf.get("save_to") or "").strip().lower()
        if scope != args.scope or save_to != args.save_to:
            continue
        filename = str(it.get("normalized_filename") or it.get("filename") or "").strip()
        if filename.startswith("subflows/"):
            v2_count += 1
        matches.append({"filename": filename, "subflow": sf})

    if not matches:
        print("No subflows found via API for scope/save_to. If you edited in the panel, it may be using a different repo or API base.")
        return 0

    layout = args.layout
    if layout == "auto":
        layout = "v2" if v2_count else "legacy"

    if out_dir is None:
        if layout == "v2":
            out_dir = Path(f"backend/app/verticals/{args.vertical}/subflows/{args.scope}/{args.save_to}")
        else:
            out_dir = Path(f"backend/app/verticals/{args.vertical}")
    out_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    for it in matches:
        filename = it["filename"]
        if not filename:
            continue
        url = f"{api_base}/v1/admin/verticals/{args.vertical}/files/{quote(filename)}"
        payload = _request_json(url, headers=headers)
        content = payload.get("content") if isinstance(payload, dict) else None
        if not isinstance(content, dict):
            print(f"Skipping {filename}: empty or invalid JSON")
            continue

        if layout == "v2" and filename.startswith("subflows/"):
            key = Path(filename).stem
            out_path = out_dir / f"{key}.json"
        else:
            out_path = out_dir / Path(filename).name

        if out_path.exists() and not args.overwrite:
            print(f"Skip existing: {out_path}")
            continue

        out_path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
        written += 1

    if args.include_flow_base:
        vertical_dir = _infer_vertical_dir(out_dir)
        flow_name = f"flow_base_scope_{args.scope}.json"
        flow_url = f"{api_base}/v1/admin/verticals/{args.vertical}/files/{quote(flow_name)}"
        try:
            flow_payload = _request_json(flow_url, headers=headers)
            flow_content = flow_payload.get("content") if isinstance(flow_payload, dict) else None
            if isinstance(flow_content, dict):
                flow_path = vertical_dir / flow_name
                if flow_path.exists() and not args.overwrite:
                    print(f"Skip existing: {flow_path}")
                else:
                    flow_path.write_text(json.dumps(flow_content, ensure_ascii=False, indent=2), encoding="utf-8")
                    print(f"Wrote {flow_path}")
        except Exception as exc:
            print(f"flow_base_scope export skipped: {exc}")

    print(f"Exported {written} subflows to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
