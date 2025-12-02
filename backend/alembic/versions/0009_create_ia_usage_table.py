"""create ia_usage table

Revision ID: 0009_create_ia_usage_table
Revises: 0008_ai_interactions_audit
Create Date: 2025-01-01 00:00:02.000000
"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg

revision = "0009_create_ia_usage_table"
down_revision = "0008_ai_interactions_audit"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "ia_usage",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "date",
            sa.Date(),
            nullable=False,
            server_default=sa.func.current_date(),
        ),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column(
            "tokens_in",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "tokens_out",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "cost_eur",
            sa.Numeric(precision=12, scale=6),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_ia_usage_tenant_id", "ia_usage", ["tenant_id"])
    op.create_index("ix_ia_usage_date", "ia_usage", ["date"])
    op.create_index("ix_ia_usage_tenant_date", "ia_usage", ["tenant_id", "date"])


def downgrade():
    op.drop_index("ix_ia_usage_tenant_date", table_name="ia_usage")
    op.drop_index("ix_ia_usage_date", table_name="ia_usage")
    op.drop_index("ix_ia_usage_tenant_id", table_name="ia_usage")
    op.drop_table("ia_usage")
