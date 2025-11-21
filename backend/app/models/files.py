import uuid

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from app.db.base import Base


class FileAsset(Base):
    __tablename__ = "files"
    __table_args__ = (sa.Index("ix_files_tenant_created", "tenant_id", "created_at"),)

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    lead_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="SET NULL"), nullable=True)
    s3_key = sa.Column(sa.String(255), nullable=False, unique=True)
    tipo = sa.Column(sa.String(30), nullable=True)
    meta = sa.Column(pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb"))
    created_at = sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
