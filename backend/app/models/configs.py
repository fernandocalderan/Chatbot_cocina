import uuid

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from app.db.base import Base


class Config(Base):
    __tablename__ = "configs"
    __table_args__ = (sa.Index("ix_configs_tenant_tipo", "tenant_id", "tipo"),)

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    tipo = sa.Column(sa.String(50), nullable=False)
    payload_json = sa.Column(pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb"))
    version = sa.Column(sa.Integer, nullable=False, server_default="1")
    created_at = sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    updated_at = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()
    )
