"""add ia_monthly_limit_eur to tenant

Revision ID: 0010_add_tenant_ia_limit
Revises: 0009_create_ia_usage_table
Create Date: 2025-01-02 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0010_add_tenant_ia_limit"
down_revision = "0009_create_ia_usage_table"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "tenants",
        sa.Column(
            "ia_monthly_limit_eur",
            sa.Numeric(precision=12, scale=2),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("tenants", "ia_monthly_limit_eur")
