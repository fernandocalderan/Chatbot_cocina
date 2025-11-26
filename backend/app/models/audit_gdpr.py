import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from app.db.base import Base


class AuditGDPR(Base):
    __tablename__ = "audit_gdpr"
    __table_args__ = (
        sa.Index("ix_audit_gdpr_tenant_created", "tenant_id", "created_at"),
    )

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    tenant_id = sa.Column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )
    entity = sa.Column(sa.String(50), nullable=False)
    entity_id = sa.Column(sa.String(64), nullable=False)
    action = sa.Column(sa.String(50), nullable=False)
    actor = sa.Column(sa.String(100), nullable=True)
    meta = sa.Column(pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb"))
    created_at = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
