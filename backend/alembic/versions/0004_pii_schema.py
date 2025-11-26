"""add pii_version columns

Revision ID: 0004_pii_schema
Revises: 0003_flow_scoring_tables
Create Date: 2025-02-09
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0004_pii_schema"
down_revision: Union[str, None] = "0003_flow_scoring_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "leads",
        sa.Column("pii_version", sa.SmallInteger(), nullable=False, server_default="1"),
    )
    op.add_column(
        "messages",
        sa.Column("pii_version", sa.SmallInteger(), nullable=False, server_default="1"),
    )


def downgrade() -> None:
    op.drop_column("messages", "pii_version")
    op.drop_column("leads", "pii_version")
