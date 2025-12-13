from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.conversation_templates import ConversationTemplate


class TemplateService:
    @staticmethod
    def list_templates(db: Session, tenant_id: str) -> list[ConversationTemplate]:
        return (
            db.query(ConversationTemplate)
            .filter(
                or_(
                    ConversationTemplate.tenant_id == tenant_id,
                    ConversationTemplate.tenant_id.is_(None),
                )
            )
            .order_by(ConversationTemplate.is_default.desc(), ConversationTemplate.created_at.desc())
            .all()
        )

    @staticmethod
    def clone_template_to_tenant(
        db: Session, template: ConversationTemplate, tenant_id: str, mark_default: bool = False
    ) -> ConversationTemplate:
        clone = ConversationTemplate(
            tenant_id=tenant_id,
            name=template.name,
            description=template.description,
            schema_json=template.schema_json,
            is_default=mark_default,
        )
        db.add(clone)
        db.commit()
        db.refresh(clone)
        return clone

    @staticmethod
    def clone_default_template(
        db: Session, tenant_id: str
    ) -> Optional[ConversationTemplate]:
        tpl = (
            db.query(ConversationTemplate)
            .filter(
                ConversationTemplate.tenant_id.is_(None),
                ConversationTemplate.is_default.is_(True),
            )
            .order_by(ConversationTemplate.created_at.asc())
            .first()
        )
        if not tpl:
            return None
        return TemplateService.clone_template_to_tenant(db, tpl, tenant_id, mark_default=True)

    @staticmethod
    def get(db: Session, template_id: str) -> Optional[ConversationTemplate]:
        return (
            db.query(ConversationTemplate)
            .filter(ConversationTemplate.id == template_id)
            .first()
        )
