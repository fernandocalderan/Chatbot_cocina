import uuid

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from app.db.base import Base


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (sa.Index("ix_appointments_tenant_slot", "tenant_id", "slot_start"),)

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    lead_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="SET NULL"), nullable=True)
    slot_start = sa.Column(sa.DateTime(timezone=True), nullable=False)
    slot_end = sa.Column(sa.DateTime(timezone=True), nullable=False)
    estado = sa.Column(sa.String(30), nullable=False, server_default="pending")
    origen = sa.Column(sa.String(30), nullable=True)
    notas = sa.Column(sa.Text, nullable=True)
    reminder_status = sa.Column(sa.String(30), nullable=True)
    created_at = sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    updated_at = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()
    )
