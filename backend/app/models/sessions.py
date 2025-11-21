import uuid

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from app.db.base import Base


class Session(Base):
    __tablename__ = "sessions"
    __table_args__ = (sa.Index("ix_sessions_tenant_user", "tenant_id", "external_user_id"),)

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    external_user_id = sa.Column(sa.String(128), nullable=True)
    canal = sa.Column(sa.String(20), nullable=False, server_default="web")
    idioma_detectado = sa.Column(sa.String(10), nullable=True)
    state = sa.Column(sa.String(50), nullable=True)
    variables_json = sa.Column(pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb"))
    last_block_id = sa.Column(sa.String(100), nullable=True)
    expires_at = sa.Column(sa.DateTime(timezone=True), nullable=True)
    created_at = sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    updated_at = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()
    )
