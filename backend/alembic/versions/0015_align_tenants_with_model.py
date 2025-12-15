"""align tenants table with model

Revision ID: 0015_align_tenants_with_model
Revises: 0014_quota_fields_and_plan_enum
Create Date: 2025-12-14
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0015_align_tenants_with_model"
down_revision = "0014_quota_fields_and_plan_enum"
branch_labels = None
depends_on = None


def upgrade():
    # ---------- SCHEDULING / AVAILABILITY ----------
    op.add_column(
        "tenants",
        sa.Column("workdays", postgresql.ARRAY(sa.Integer()), nullable=True),
    )
    op.add_column(
        "tenants",
        sa.Column("slot_duration", sa.Integer(), nullable=True),
    )
    op.add_column(
        "tenants",
        sa.Column("opening_hours", postgresql.JSONB(), nullable=True),
    )

    # ---------- USAGE / QUOTAS ----------
    op.add_column(
        "tenants",
        sa.Column(
            "usage_mode",
            sa.Enum("ACTIVE", "SAVING", "LOCKED", name="usage_mode"),
            nullable=False,
            server_default="ACTIVE",
        ),
    )
    op.add_column(
        "tenants",
        sa.Column(
            "usage_monthly",
            sa.Float(),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "tenants",
        sa.Column(
            "usage_reset_day",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
    )
    op.add_column(
        "tenants",
        sa.Column(
            "needs_upgrade_notice",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    # ---------- IA / PLAN ----------
    op.add_column(
        "tenants",
        sa.Column(
            "ia_plan",
            sa.Enum("BASE", "PRO", "ELITE", name="plan_enum"),
            nullable=True,
        ),
    )

    # ---------- TEMPLATES ----------
    op.add_column(
        "tenants",
        sa.Column(
            "default_template_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("tenants", "default_template_id")
    op.drop_column("tenants", "ia_plan")
    op.drop_column("tenants", "needs_upgrade_notice")
    op.drop_column("tenants", "usage_reset_day")
    op.drop_column("tenants", "usage_monthly")
    op.drop_column("tenants", "usage_mode")
    op.drop_column("tenants", "opening_hours")
    op.drop_column("tenants", "slot_duration")
    op.drop_column("tenants", "workdays")
