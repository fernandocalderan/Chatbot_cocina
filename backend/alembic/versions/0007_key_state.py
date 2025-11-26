"""add key_state table

Revision ID: 0007_key_state
Revises: 0006_audit_gdpr
Create Date: 2025-02-09
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

# revision identifiers, used by Alembic.
revision: str = "0007_key_state"
down_revision: Union[str, None] = "0006_audit_gdpr"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "key_state",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("current_kid", sa.String(50), nullable=True),
        sa.Column("meta", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
    )


def downgrade() -> None:
    op.drop_table("key_state")
