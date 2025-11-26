import uuid

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from app.db.base import Base


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        sa.Index("ix_tasks_tenant_owner_status", "tenant_id", "owner_id", "status"),
    )

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    lead_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="SET NULL"), nullable=True)
    owner_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    title = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    status = sa.Column(sa.String(30), nullable=False, server_default="pendiente")
    due_date = sa.Column(sa.DateTime(timezone=True), nullable=True)
    priority = sa.Column(sa.String(10), nullable=False, server_default="media")
    created_at = sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    completed_at = sa.Column(sa.DateTime(timezone=True), nullable=True)
