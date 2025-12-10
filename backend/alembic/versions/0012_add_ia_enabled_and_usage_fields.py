"""add ia_enabled flag and ia_usage context fields"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0012_add_ia_enabled_and_usage_fields"
down_revision = "0011_add_billing_fields"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "tenants",
        sa.Column(
            "ia_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )
    op.add_column(
        "ia_usage",
        sa.Column("session_id", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "ia_usage",
        sa.Column("call_type", sa.String(length=32), nullable=True),
    )
    op.create_index(
        "ix_ia_usage_session_id", "ia_usage", ["session_id"], unique=False
    )


def downgrade():
    op.drop_index("ix_ia_usage_session_id", table_name="ia_usage")
    op.drop_column("ia_usage", "call_type")
    op.drop_column("ia_usage", "session_id")
    op.drop_column("tenants", "ia_enabled")
