import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from app.db.base import Base


class AIInteractionAudit(Base):
    __tablename__ = "ai_interactions_audit"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    tenant_id = sa.Column(sa.String(64), nullable=True, index=True)
    flow = sa.Column(sa.String(64), nullable=True)
    input_masked = sa.Column(sa.Text, nullable=True)
    output_masked = sa.Column(sa.Text, nullable=True)
    moderation_blocked = sa.Column(sa.Boolean, nullable=False, server_default=sa.text("false"))
    moderation_adjusted = sa.Column(sa.Boolean, nullable=False, server_default=sa.text("false"))
    circuit_breaker = sa.Column(sa.Boolean, nullable=False, server_default=sa.text("false"))
    latency_ms = sa.Column(sa.Float, nullable=True)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())

