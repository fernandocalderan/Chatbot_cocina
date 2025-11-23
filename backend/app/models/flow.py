import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from app.db.base import Base


class Flow(Base):
    __tablename__ = "flow"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    data = sa.Column(pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb"))
    updated_at = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()
    )


class Scoring(Base):
    __tablename__ = "scoring"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    data = sa.Column(pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb"))
    updated_at = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()
    )
