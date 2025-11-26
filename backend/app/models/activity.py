import uuid

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from app.db.base import Base


class Activity(Base):
    __tablename__ = "activities"
    __table_args__ = (sa.Index("ix_activities_lead_created", "lead_id", "created_at"),)

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    lead_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    user_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    type = sa.Column(sa.String(30), nullable=False)
    content = sa.Column(sa.String(500), nullable=False)
    meta = sa.Column(pg.JSONB, nullable=True)
    created_at = sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
