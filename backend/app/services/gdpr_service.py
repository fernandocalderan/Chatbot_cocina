from __future__ import annotations

import time
from typing import Optional

from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.leads import Lead
from app.models.messages import Message
from app.models.files import FileAsset
from app.models.appointments import Appointment
from app.models.sessions import Session as DBSess
from app.models.task import Task
from app.models.activity import Activity
from app.models.audit_gdpr import AuditGDPR
from app.services.file_service import FileService
from app.services.pii_service import PIIService


class GDPRService:
    def __init__(self, db: Session):
        self.db = db
        self.file_service = FileService()
        self.pii = PIIService()

    def _audit(
        self,
        tenant_id: str,
        entity: str,
        entity_id: str,
        action: str,
        actor: Optional[str] = None,
        meta: Optional[dict] = None,
    ):
        try:
            log = AuditGDPR(
                tenant_id=tenant_id,
                entity=entity,
                entity_id=entity_id,
                action=action,
                actor=actor,
                meta=meta or {},
            )
            self.db.add(log)
            self.db.commit()
        except Exception as exc:
            self.db.rollback()
            logger.warning({"event": "audit_gdpr_failed", "error": str(exc)})

    def forget_lead(
        self, tenant_id: str, lead_id: str, actor: Optional[str] = None
    ) -> bool:
        start = time.perf_counter()
        lead = (
            self.db.query(Lead)
            .filter(Lead.id == lead_id, Lead.tenant_id == tenant_id)
            .first()
        )
        if not lead:
            return False
        # Delete messages for the lead's session
        if lead.session_id:
            try:
                self.db.query(Message).filter(
                    Message.tenant_id == tenant_id,
                    Message.session_id == lead.session_id,
                ).delete(synchronize_session=False)
            except SQLAlchemyError:
                self.db.rollback()
        # Anonymize lead metadata
        anon_meta = {
            "contact_name": "anonimo",
            "contact_email": "",
            "contact_phone": "",
            "contact_address": "",
        }
        encrypted_meta, _ = self.pii.encrypt_meta(anon_meta, tenant_id)
        lead.meta_data = encrypted_meta
        lead.pii_version = 1
        self.db.add(lead)
        # Delete files
        self._delete_lead_files(tenant_id, lead_id)
        try:
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            return False
        self._audit(
            tenant_id,
            "lead",
            lead_id,
            "gdpr_forget",
            actor,
            {"duration_ms": round((time.perf_counter() - start) * 1000, 2)},
        )
        return True

    def purge_tenant(self, tenant_id: str, actor: Optional[str] = None) -> bool:
        start = time.perf_counter()
        try:
            lead_ids = [
                str(lead_row.id)
                for lead_row in self.db.query(Lead.id)
                .filter(Lead.tenant_id == tenant_id)
                .all()
            ]
            for lid in lead_ids:
                self._delete_lead_files(tenant_id, lid)
            self.db.query(Message).filter(Message.tenant_id == tenant_id).delete(
                synchronize_session=False
            )
            self.db.query(Appointment).filter(
                Appointment.tenant_id == tenant_id
            ).delete(synchronize_session=False)
            self.db.query(Task).filter(Task.tenant_id == tenant_id).delete(
                synchronize_session=False
            )
            self.db.query(Activity).filter(Activity.tenant_id == tenant_id).delete(
                synchronize_session=False
            )
            self.db.query(FileAsset).filter(FileAsset.tenant_id == tenant_id).delete(
                synchronize_session=False
            )
            self.db.query(DBSess).filter(DBSess.tenant_id == tenant_id).delete(
                synchronize_session=False
            )
            self.db.query(Lead).filter(Lead.tenant_id == tenant_id).delete(
                synchronize_session=False
            )
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            return False
        self._audit(
            tenant_id,
            "tenant",
            tenant_id,
            "gdpr_purge",
            actor,
            {"duration_ms": round((time.perf_counter() - start) * 1000, 2)},
        )
        return True

    def export_lead(self, tenant_id: str, lead_id: str) -> Optional[dict]:
        lead = (
            self.db.query(Lead)
            .filter(Lead.id == lead_id, Lead.tenant_id == tenant_id)
            .first()
        )
        if not lead:
            return None
        meta = self.pii.decrypt_meta(lead.meta_data or {})
        messages = (
            self.db.query(Message)
            .filter(
                Message.tenant_id == tenant_id, Message.session_id == lead.session_id
            )
            .order_by(Message.id.asc())
            .all()
            if lead.session_id
            else []
        )
        msg_items = []
        for m in messages:
            content = m.content
            if self.pii.is_encrypted(content):
                content = self.pii.decrypt_pii(content)
            msg_items.append(
                {"role": m.role, "content": content, "created_at": m.created_at}
            )
        self._audit(tenant_id, "lead", lead_id, "gdpr_export", None, {})
        return {
            "lead": {"id": str(lead.id), "metadata": meta, "status": lead.status},
            "messages": msg_items,
        }

    def _delete_lead_files(self, tenant_id: str, lead_id: str):
        try:
            self.file_service.delete_lead_files(tenant_id, lead_id)
        except Exception as exc:
            logger.warning({"event": "gdpr_file_delete_failed", "error": str(exc)})
