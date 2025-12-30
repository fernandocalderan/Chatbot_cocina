import uuid

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from app.db.base import Base


class FlowGeneration(Base):
    __tablename__ = "flow_generations"
    __table_args__ = (
        sa.Index("ix_flow_generations_tenant_created", "tenant_id", "created_at"),
        sa.Index("ix_flow_generations_tenant_status", "tenant_id", "status"),
    )

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    status = sa.Column(sa.String(20), nullable=False, server_default="queued")
    source = sa.Column(sa.String(30), nullable=True)  # tenant_panel|migration|admin

    requested_by_user_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    scopes = sa.Column(pg.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb"))
    languages = sa.Column(pg.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb"))
    selected_file_ids = sa.Column(pg.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb"))

    model = sa.Column(sa.String(100), nullable=True)
    tokens_in = sa.Column(sa.Integer, nullable=False, server_default="0")
    tokens_out = sa.Column(sa.Integer, nullable=False, server_default="0")
    cost_eur = sa.Column(sa.Numeric(precision=12, scale=6), nullable=False, server_default="0")

    result_flow_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("flows.id", ondelete="SET NULL"), nullable=True)
    error = sa.Column(sa.Text, nullable=True)
    meta = sa.Column(pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb"))

    created_at = sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())

