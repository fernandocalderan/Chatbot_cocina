"""merge heads: customer_code + verticals/flows

Revision ID: 0018_merge_heads_customer_code_and_verticals
Revises: 0012_customer_code, 0017_add_flow_mode_and_active_flow_id
Create Date: 2025-12-17 20:55:00.000000
"""

from alembic import op  # noqa: F401


revision = "0018_merge_heads_customer_code_and_verticals"
down_revision = ("0012_customer_code", "0017_add_flow_mode_and_active_flow_id")
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Merge revision: no-op
    return


def downgrade() -> None:
    # Merge revision: no-op
    return

