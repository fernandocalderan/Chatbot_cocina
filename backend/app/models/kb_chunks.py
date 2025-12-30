import uuid

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from pgvector.sqlalchemy import Vector

from app.db.base import Base


class KBChunk(Base):
    __tablename__ = "kb_chunks"
    __table_args__ = (
        sa.Index("ix_kb_chunks_tenant_file", "tenant_id", "file_id"),
        sa.Index("ix_kb_chunks_tenant_created", "tenant_id", "created_at"),
    )

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    file_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("files.id", ondelete="CASCADE"), nullable=False)

    chunk_idx = sa.Column(sa.Integer, nullable=False)
    text = sa.Column(sa.Text, nullable=False)
    embedding = sa.Column(Vector(1536), nullable=False)
    meta = sa.Column(pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb"))

    created_at = sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())

