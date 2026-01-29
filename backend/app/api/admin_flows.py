from datetime import datetime, timezone
import json

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import sqlalchemy as sa

from app.api.deps import get_db
from app.middleware.authz import require_role
from app.models.flows import Flow as FlowVersioned
from app.models.users import UserRole

router = APIRouter(
    prefix="/admin/flows",
    tags=["admin"],
    dependencies=[Depends(require_role(UserRole.SUPER_ADMIN.value))],
)


def _next_version_for_group(
    db: Session,
    *,
    owner_type: str,
    owner_id: str | None,
    vertical_key: str | None,
    scope_key: str | None,
    flow_kind: str,
) -> int:
    q = db.query(sa.func.max(FlowVersioned.version)).filter(
        FlowVersioned.owner_type == owner_type,
        FlowVersioned.flow_kind == flow_kind,
    )
    if owner_id:
        q = q.filter(FlowVersioned.owner_id == owner_id)
    else:
        q = q.filter(FlowVersioned.owner_id.is_(None))
    if vertical_key:
        q = q.filter(FlowVersioned.vertical_key == vertical_key)
    if scope_key:
        q = q.filter(FlowVersioned.scope_key == scope_key)
    current = q.scalar() or 0
    return int(current) + 1


@router.post("/import")
def import_flow_base(
    file: UploadFile = File(...),
    vertical_key: str = Form(...),
    scope_key: str = Form(...),
    flow_kind: str = Form("base"),
    owner_type: str = Form("TENANT"),
    owner_id: str | None = Form(None),
    db: Session = Depends(get_db),
):
    try:
        raw = file.file.read()
        content = raw.decode("utf-8")
        data = json.loads(content)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid_json")

    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="invalid_flow_schema")
    if not isinstance(data.get("blocks"), dict) or not data.get("blocks"):
        raise HTTPException(status_code=400, detail="missing_blocks")
    if not data.get("start_block"):
        raise HTTPException(status_code=400, detail="missing_start_block")

    owner_type_norm = str(owner_type or "TENANT").upper()
    if owner_type_norm not in {"TENANT", "GLOBAL"}:
        raise HTTPException(status_code=400, detail="invalid_owner_type")

    tenant_id = None
    if owner_type_norm == "TENANT":
        if not owner_id:
            raise HTTPException(status_code=400, detail="missing_owner_id")
        tenant_id = owner_id

    next_version = _next_version_for_group(
        db,
        owner_type=owner_type_norm,
        owner_id=owner_id if owner_type_norm == "TENANT" else None,
        vertical_key=vertical_key,
        scope_key=scope_key,
        flow_kind=flow_kind,
    )

    new_flow = FlowVersioned(
        tenant_id=tenant_id,
        vertical_key=str(vertical_key),
        scope_key=str(scope_key),
        version=next_version,
        schema_json=data,
        estado="draft",
        published_at=None,
        owner_type=owner_type_norm,
        owner_id=owner_id if owner_type_norm == "TENANT" else None,
        flow_kind=str(flow_kind or "base"),
    )
    db.add(new_flow)
    db.commit()
    db.refresh(new_flow)
    return {
        "flow_id": str(new_flow.id),
        "version": new_flow.version,
        "estado": new_flow.estado,
        "owner_type": new_flow.owner_type,
        "owner_id": str(new_flow.owner_id) if new_flow.owner_id else None,
        "vertical_key": new_flow.vertical_key,
        "scope_key": new_flow.scope_key,
        "flow_kind": new_flow.flow_kind,
    }


@router.post("/{flow_id}/publish")
def publish_flow_by_id(flow_id: str, db: Session = Depends(get_db)):
    flow = db.query(FlowVersioned).filter(FlowVersioned.id == flow_id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="flow_not_found")

    owner_type = str(getattr(flow, "owner_type", "") or "TENANT").upper()
    owner_id = getattr(flow, "owner_id", None)
    vertical_key = getattr(flow, "vertical_key", None)
    scope_key = getattr(flow, "scope_key", None)
    flow_kind = str(getattr(flow, "flow_kind", "") or "base")

    q = db.query(FlowVersioned).filter(
        FlowVersioned.owner_type == owner_type,
        FlowVersioned.flow_kind == flow_kind,
    )
    if owner_id:
        q = q.filter(FlowVersioned.owner_id == owner_id)
    else:
        q = q.filter(FlowVersioned.owner_id.is_(None))
    if vertical_key:
        q = q.filter(FlowVersioned.vertical_key == vertical_key)
    if scope_key:
        q = q.filter(FlowVersioned.scope_key == scope_key)
    q.update({"estado": "draft", "published_at": None})

    flow.estado = "published"
    flow.published_at = datetime.now(timezone.utc)
    db.add(flow)
    db.commit()
    db.refresh(flow)
    return {
        "flow_id": str(flow.id),
        "version": flow.version,
        "estado": flow.estado,
        "published_at": flow.published_at.isoformat() if flow.published_at else None,
    }
