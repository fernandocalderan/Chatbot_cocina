import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from loguru import logger

from app.api.auth import oauth2_scheme, require_auth
from app.api.deps import get_db, get_tenant_id
from app.core.config import get_settings
from app.models.files import FileAsset
from app.models.leads import Lead
from app.models.tenants import Tenant
from app.services.file_service import FileService
from app.services.file_text_extractor import (
    extract_image_text_via_openai,
    extract_pdf_text,
    preview,
    write_extracted_text,
)

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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="unsupported_file_type"
        )

    settings = get_settings()
    base_dir = Path(settings.storage_dir)
    base_dir.mkdir(parents=True, exist_ok=True)

    # Resolver lead_id por session_id si no llega explícito
    resolved_lead_id: Optional[str] = None
    if lead_id:
        lead = (
            db.query(Lead)
            .filter(Lead.id == lead_id, Lead.tenant_id == tenant_id)
            .first()
        )
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="lead_not_found"
            )
        resolved_lead_id = str(lead.id)
    elif session_id:
        lead = (
            db.query(Lead)
            .filter(Lead.session_id == session_id, Lead.tenant_id == tenant_id)
            .first()
        )
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

    # Extracción básica para PDFs (sin IA) para poder usarlo como material/KB.
    if file.content_type == "application/pdf":
        extracted = extract_pdf_text(dest_path)
        out_path = write_extracted_text(dest_path, extracted)
        if out_path:
            meta["extracted_text_key"] = str(out_path.relative_to(base_dir))
            meta["extracted_preview"] = preview(extracted)
            meta["extracted_method"] = "pypdf"

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
        "extracted": bool(meta.get("extracted_text_key")),
    }


@router.get("", dependencies=[Depends(require_auth)])
def list_files(
    session_id: str | None = None,
    lead_id: str | None = None,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    q = db.query(FileAsset).filter(FileAsset.tenant_id == tenant_id)
    if session_id:
        q = q.filter(FileAsset.meta["session_id"].astext == session_id)  # type: ignore[index]
    if lead_id:
        q = q.filter(FileAsset.lead_id == lead_id)
    rows = q.order_by(FileAsset.created_at.desc()).limit(200).all()
    items = []
    for r in rows:
        meta = r.meta or {}
        items.append(
            {
                "file_id": str(r.id),
                "lead_id": str(r.lead_id) if r.lead_id else None,
                "s3_key": r.s3_key,
                "content_type": r.tipo,
                "original_filename": meta.get("original_filename"),
                "size_bytes": meta.get("size_bytes"),
                "session_id": meta.get("session_id"),
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "extracted_text_key": meta.get("extracted_text_key"),
                "extracted_preview": meta.get("extracted_preview"),
                "extracted_method": meta.get("extracted_method"),
            }
        )
    return {"items": items}


@router.post("/{file_id}/extract", dependencies=[Depends(require_auth)])
def extract_file_text(
    file_id: str,
    use_ai: bool = False,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    asset = db.query(FileAsset).filter(FileAsset.id == file_id, FileAsset.tenant_id == tenant_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="file_not_found")

    settings = get_settings()
    base_dir = Path(settings.storage_dir)
    file_path = base_dir / str(asset.s3_key)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="storage_file_not_found")

    meta = asset.meta or {}
    content_type = str(asset.tipo or meta.get("content_type") or "")

    extracted = ""
    method = None
    if content_type == "application/pdf":
        extracted = extract_pdf_text(file_path)
        method = "pypdf"
    elif content_type in {"image/png", "image/jpeg"} and use_ai:
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="tenant_not_found")
        extracted = extract_image_text_via_openai(
            file_path,
            content_type=content_type,
            tenant=tenant,
            tenant_id=str(tenant_id),
            db=db,
            session_id=str(meta.get("session_id") or "") or None,
        )
        method = "openai_vision"

    out_path = write_extracted_text(file_path, extracted)
    if out_path:
        meta["extracted_text_key"] = str(out_path.relative_to(base_dir))
        meta["extracted_preview"] = preview(extracted)
        meta["extracted_method"] = method
        asset.meta = meta
        db.add(asset)
        db.commit()
        db.refresh(asset)
        return {"file_id": str(asset.id), "extracted": True, "method": method, "preview": meta.get("extracted_preview")}

    raise HTTPException(status_code=400, detail="extraction_not_available")


@router.get("/{lead_id}/comercial.pdf", dependencies=[Depends(require_auth)])
def download_comercial_pdf(
    lead_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    return _download_pdf(lead_id, "comercial", db, tenant_id)


@router.get("/{lead_id}/operativo.pdf", dependencies=[Depends(require_auth)])
def download_operativo_pdf(
    lead_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    return _download_pdf(lead_id, "operativo", db, tenant_id)


def _download_pdf(lead_id: str, tipo: str, db, tenant_id: str):
    lead = (
        db.query(Lead).filter(Lead.id == lead_id, Lead.tenant_id == tenant_id).first()
    )
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="lead_not_found"
        )
    fs = FileService()
    key = f"tenants/{tenant_id}/leads/{lead_id}/{tipo}.pdf"
    content = fs.download_pdf(key)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="file_not_found"
        )
    logger.info(
        {
            "tenant_id": tenant_id,
            "lead_id": lead_id,
            "tipo_pdf": tipo,
            "plan": getattr(getattr(lead, "tenant", None), "plan", None)
            or getattr(getattr(lead, "tenant", None), "ia_plan", None),
            "success": True,
            "latency_ms": 0.0,
            "s3_key": key,
        }
    )
    return FileResponse(
        path=fs.base_dir / key,
        media_type="application/pdf",
        filename=f"{tipo}.pdf",
        headers={"X-Tenant-ID": tenant_id},
    )
