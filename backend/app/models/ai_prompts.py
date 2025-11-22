import uuid

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from app.db.base import Base


class AiPrompt(Base):
    __tablename__ = "ai_prompts"
    __table_args__ = (sa.UniqueConstraint("tenant_id", "name", "version", name="uq_prompt_tenant_name_version"),)

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True)
    name = sa.Column(sa.String(100), nullable=False)
    version = sa.Column(sa.Integer, nullable=False)
    prompt_text = sa.Column(sa.Text, nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
