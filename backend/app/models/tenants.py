import uuid

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from app.db.base import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = sa.Column(sa.String(255), nullable=False, index=True)
    contact_email = sa.Column(sa.String(320), nullable=True)
    plan = sa.Column(sa.String(50), nullable=False, server_default="Base")
    flags_ia = sa.Column(pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb"))
    branding = sa.Column(pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb"))
    idioma_default = sa.Column(sa.String(10), nullable=False, server_default="es")
    timezone = sa.Column(sa.String(64), nullable=False, server_default="Europe/Madrid")
    created_at = sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    updated_at = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()
    )
