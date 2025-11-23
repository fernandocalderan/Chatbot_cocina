import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from app.api.auth import oauth2_scheme, require_auth

router = APIRouter(prefix="/scoring", tags=["scoring"])
_FLOW_PATH = Path(__file__).resolve().parent.parent / "flows" / "base_flow.json"


def _load_flow() -> dict:
    with _FLOW_PATH.open() as f:
        return json.load(f)


def _save_flow(data: dict):
    with _FLOW_PATH.open("w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


@router.post("/update", dependencies=[Depends(require_auth)])
def update_scoring(payload: dict, token: str = Depends(oauth2_scheme)):
    try:
        flow = _load_flow()
        flow["scoring"] = payload
        _save_flow(flow)
        return {"status": "updated", "scoring": payload}
    except Exception as exc:  # pragma: no cover - simple guard
        raise HTTPException(status_code=500, detail=f"error_updating_scoring: {exc}")
