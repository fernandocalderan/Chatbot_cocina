import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from app.db.base import Base


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        sa.Index("ix_messages_session_created", "session_id", "created_at"),
    )

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    tenant_id = sa.Column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_id = sa.Column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    role = sa.Column(sa.String(20), nullable=False)
    content = sa.Column(sa.Text, nullable=False)
    block_id = sa.Column(sa.String(100), nullable=True)
    pii_version = sa.Column(sa.SmallInteger, nullable=False, server_default="1")
    ai_meta = sa.Column(pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb"))
    attachments = sa.Column(
        pg.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")
    )
    created_at = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
