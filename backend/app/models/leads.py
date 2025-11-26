import uuid

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from app.db.base import Base


class Lead(Base):
    __tablename__ = "leads"
    __table_args__ = (
        sa.Index("ix_leads_tenant_created", "tenant_id", "created_at"),
        sa.Index("ix_leads_status", "status"),
    )

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = sa.Column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_id = sa.Column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("sessions.id", ondelete="SET NULL"),
        nullable=True,
    )
    origen = sa.Column(sa.String(50), nullable=True)
    status = sa.Column(sa.String(50), nullable=False, server_default="nuevo")
    pii_version = sa.Column(sa.SmallInteger, nullable=False, server_default="1")
    owner_id = sa.Column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    source = sa.Column(sa.String(100), nullable=True)
    lost_reason = sa.Column(sa.String(255), nullable=True)
    expected_value = sa.Column(sa.Numeric(precision=12, scale=2), nullable=True)
    closed_at = sa.Column(sa.DateTime(timezone=True), nullable=True)
    score = sa.Column(sa.Integer, nullable=True)
    score_breakdown_json = sa.Column(
        pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")
    )
    meta_data = sa.Column(
        "metadata", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")
    )
    idioma = sa.Column(sa.String(10), nullable=True)
    timezone = sa.Column(sa.String(64), nullable=True)
    created_at = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    )
