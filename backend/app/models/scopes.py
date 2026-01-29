import uuid

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from app.db.base import Base


class Scope(Base):
    __tablename__ = "scopes"
    __table_args__ = (sa.UniqueConstraint("vertical_key", "scope_key", name="uq_scopes_vertical_scope"),)

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vertical_key = sa.Column(sa.String(64), nullable=False, index=True)
    scope_key = sa.Column(sa.String(64), nullable=False)
    display_name = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    created_at = sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    updated_at = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()
    )
