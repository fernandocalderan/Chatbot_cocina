from __future__ import annotations
from pathlib import Path
from typing import Optional

from loguru import logger

from app.core.config import get_settings


class FileService:
    def __init__(self, base_dir: Optional[str] = None):
        self.settings = get_settings()
        storage_dir = base_dir or self.settings.storage_dir
        self.base_dir = Path(storage_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def upload_pdf(
        self, tenant_id: str, lead_id: str, file_bytes: bytes, tipo: str
    ) -> str:
        if tipo not in {"comercial", "operativo"}:
            raise ValueError("invalid_tipo")
        key_path = Path(f"tenants/{tenant_id}/leads/{lead_id}/{tipo}.pdf")
        dest = self.base_dir / key_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("wb") as f:
            f.write(file_bytes)
        logger.info(
            {
                "tenant_id": tenant_id,
                "lead_id": lead_id,
                "action": "upload_pdf",
                "tipo_pdf": tipo,
                "s3_key": str(key_path),
                "success": True,
            }
        )
        return str(key_path)

    def download_pdf(self, key: str) -> Optional[bytes]:
        path = self.base_dir / key
        if not path.exists():
            return None
        return path.read_bytes()

    def delete_lead_files(self, tenant_id: str, lead_id: str):
        lead_folder = self.base_dir / f"tenants/{tenant_id}/leads/{lead_id}"
        if not lead_folder.exists():
            return
        for path in lead_folder.rglob("*"):
            try:
                path.unlink()
            except Exception:
                continue
        try:
            lead_folder.rmdir()
        except Exception:
            pass
