import uuid

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from app.db.base import Base


class TenantFlowOverride(Base):
    __tablename__ = "tenant_flow_overrides"
    __table_args__ = (
        sa.UniqueConstraint("tenant_id", "base_flow_id", name="uq_tenant_base_flow_override"),
    )

    flow_id = sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    base_flow_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("flows.id", ondelete="CASCADE"), nullable=False)
    draft_json = sa.Column(pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb"))
    published = sa.Column(sa.Boolean, nullable=False, server_default=sa.text("false"))
    published_at = sa.Column(sa.DateTime(timezone=True), nullable=True)
    created_at = sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    updated_at = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()
    )
