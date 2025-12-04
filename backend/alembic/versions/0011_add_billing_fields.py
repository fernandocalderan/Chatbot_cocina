"""add billing status and stripe ids to tenants

Revision ID: 0011_add_billing_fields
Revises: 0010_add_tenant_ia_limit
Create Date: 2025-01-03 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0011_add_billing_fields"
down_revision = "0010_add_tenant_ia_limit"
branch_labels = None
depends_on = None


def upgrade():
    billing_status = sa.Enum(
        "ACTIVE", "PAST_DUE", "CANCELED", "INCOMPLETE", name="billing_status"
    )
    billing_status.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "tenants",
        sa.Column(
            "billing_status",
            billing_status,
            nullable=True,
            server_default="ACTIVE",
        ),
    )
    op.add_column(
        "tenants", sa.Column("stripe_customer_id", sa.String(length=255), nullable=True)
    )
    op.add_column(
        "tenants",
        sa.Column("stripe_subscription_id", sa.String(length=255), nullable=True),
    )


def downgrade():
    op.drop_column("tenants", "stripe_subscription_id")
    op.drop_column("tenants", "stripe_customer_id")
    op.drop_column("tenants", "billing_status")
    sa.Enum(
        "ACTIVE", "PAST_DUE", "CANCELED", "INCOMPLETE", name="billing_status"
    ).drop(op.get_bind(), checkfirst=True)
