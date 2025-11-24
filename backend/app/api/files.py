import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.auth import oauth2_scheme, require_auth
from app.api.deps import get_db, get_tenant_id
from app.core.config import get_settings
from app.models.files import FileAsset
from app.models.leads import Lead

router = APIRouter(prefix="/files", tags=["files"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "application/pdf"}
ALLOWED_EXT = {"image/jpeg": ".jpg", "image/png": ".png", "application/pdf": ".pdf"}


@router.post("/upload", dependencies=[Depends(require_auth)])
async def upload_file(
    session_id: str | None = None,
    lead_id: str | None = None,
    file: UploadFile = File(...),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="unsupported_file_type")

    settings = get_settings()
    base_dir = Path(settings.storage_dir)
    base_dir.mkdir(parents=True, exist_ok=True)

    # Resolver lead_id por session_id si no llega explícito
    resolved_lead_id: Optional[str] = None
    if lead_id:
        lead = db.query(Lead).filter(Lead.id == lead_id, Lead.tenant_id == tenant_id).first()
        if not lead:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="lead_not_found")
        resolved_lead_id = str(lead.id)
    elif session_id:
        lead = db.query(Lead).filter(Lead.session_id == session_id, Lead.tenant_id == tenant_id).first()
        if lead:
            resolved_lead_id = str(lead.id)

    ext = ALLOWED_EXT.get(file.content_type, "")
    random_name = f"{uuid.uuid4()}{ext}"
    folder = base_dir / tenant_id / (session_id or "general")
    folder.mkdir(parents=True, exist_ok=True)
    dest_path = folder / random_name

    content = await file.read()
    try:
        with dest_path.open("wb") as f:
            f.write(content)
    except OSError:
        raise HTTPException(status_code=500, detail="storage_error")

    s3_key = str(dest_path.relative_to(base_dir))
    meta = {
        "original_filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": len(content),
        "session_id": session_id,
    }

    try:
        asset = FileAsset(
            tenant_id=tenant_id,
            lead_id=resolved_lead_id,
            s3_key=s3_key,
            tipo=file.content_type,
            meta=meta,
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)
    except Exception:
        db.rollback()
        raise

    return {
        "file_id": str(asset.id),
        "tenant_id": tenant_id,
        "lead_id": resolved_lead_id,
        "session_id": session_id,
        "s3_key": s3_key,
        "content_type": file.content_type,
        "size_bytes": len(content),
    }
