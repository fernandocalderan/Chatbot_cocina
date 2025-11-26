"""ai interactions audit

Revision ID: 0008_ai_interactions_audit
Revises: 0007_key_state
Create Date: 2025-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0008_ai_interactions_audit"
down_revision = "0007_key_state"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "ai_interactions_audit",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.String(length=64), nullable=True),
        sa.Column("flow", sa.String(length=64), nullable=True),
        sa.Column("input_masked", sa.Text(), nullable=True),
        sa.Column("output_masked", sa.Text(), nullable=True),
        sa.Column(
            "moderation_blocked",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "moderation_adjusted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "circuit_breaker",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("latency_ms", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_ai_interactions_audit_tenant_id",
        "ai_interactions_audit",
        ["tenant_id"],
    )


def downgrade():
    op.drop_index("ix_ai_interactions_audit_tenant_id", table_name="ai_interactions_audit")
    op.drop_table("ai_interactions_audit")
