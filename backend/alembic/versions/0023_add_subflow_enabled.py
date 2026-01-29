"""add subflow enabled flag

Revision ID: 0023_add_subflow_enabled
Revises: 0022_add_subflows_and_routing_fields
Create Date: 2026-01-29
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0023_add_subflow_enabled"
down_revision = "0022_add_subflows_and_routing_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "flows",
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )


def downgrade() -> None:
    op.drop_column("flows", "enabled")
