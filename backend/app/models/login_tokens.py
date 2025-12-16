import uuid
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from app.db.base import Base


class LoginToken(Base):
    __tablename__ = "login_tokens"
    __table_args__ = (sa.UniqueConstraint("token_hash", name="uq_login_token_hash"),)

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = sa.Column(sa.String(128), nullable=False)
    jti = sa.Column(sa.String(64), nullable=True)
    expires_at = sa.Column(sa.DateTime(timezone=True), nullable=False)
    used_at = sa.Column(sa.DateTime(timezone=True), nullable=True)
    created_at = sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
