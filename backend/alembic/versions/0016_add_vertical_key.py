"""add vertical_key to tenants

Revision ID: 0016_add_vertical_key
Revises: 0015_align_tenants_with_model
Create Date: 2025-02-10 10:20:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0016_add_vertical_key"
down_revision = "0015_align_tenants_with_model"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tenants", sa.Column("vertical_key", sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column("tenants", "vertical_key")
