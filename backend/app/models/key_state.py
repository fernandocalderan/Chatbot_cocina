import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from app.db.base import Base


class KeyState(Base):
    __tablename__ = "key_state"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    type = sa.Column(sa.String(20), nullable=False)  # jwt or pii
    current_kid = sa.Column(sa.String(50), nullable=True)
    meta = sa.Column(pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb"))
