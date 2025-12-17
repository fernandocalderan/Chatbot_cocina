import uuid

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from app.db.base import Base


class Flow(Base):
    __tablename__ = "flows"
    __table_args__ = (sa.UniqueConstraint("tenant_id", "version", name="uq_flow_version_per_tenant"),)

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    vertical_key = sa.Column(sa.String(64), nullable=True)
    version = sa.Column(sa.Integer, nullable=False)
    schema_json = sa.Column(pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb"))
    estado = sa.Column(sa.String(30), nullable=False, server_default="draft")
    published_at = sa.Column(sa.DateTime(timezone=True), nullable=True)
    rollback_to_version = sa.Column(sa.Integer, nullable=True)
    created_at = sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    updated_at = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()
    )
