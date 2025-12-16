import uuid
from enum import Enum

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from app.db.base import Base


class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    AGENT = "AGENT"
    INTERNAL = "INTERNAL"


class User(Base):
    __tablename__ = "users"
    __table_args__ = (sa.UniqueConstraint("tenant_id", "email", name="uq_user_email_tenant"),)

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    email = sa.Column(sa.String(320), nullable=False)
    hashed_password = sa.Column(sa.String(255), nullable=True)
    role = sa.Column(sa.String(50), nullable=False, server_default=UserRole.ADMIN.value)
    status = sa.Column(sa.String(50), nullable=False, server_default="ACTIVE")
    must_set_password = sa.Column(sa.Boolean, nullable=False, server_default=sa.text("true"))
    mfa_enabled = sa.Column(sa.Boolean, nullable=False, server_default=sa.text("false"))
    created_at = sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    updated_at = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()
    )
