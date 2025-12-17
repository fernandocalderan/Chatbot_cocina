"""add flow_mode/active_flow_id + flows.vertical_key

Revision ID: 0017_add_flow_mode_and_active_flow_id
Revises: 0016_add_vertical_key
Create Date: 2025-12-17 20:50:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg


# revision identifiers, used by Alembic.
revision = "0017_add_flow_mode_and_active_flow_id"
down_revision = "0016_add_vertical_key"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tenants", sa.Column("flow_mode", sa.String(length=32), nullable=False, server_default="LEGACY"))
    op.add_column("tenants", sa.Column("active_flow_id", pg.UUID(as_uuid=True), nullable=True))
    op.add_column("flows", sa.Column("vertical_key", sa.String(length=64), nullable=True))

    # Si el tenant ya tiene vertical_key, lo consideramos VERTICAL por defecto.
    op.execute("UPDATE tenants SET flow_mode = 'VERTICAL' WHERE vertical_key IS NOT NULL")


def downgrade() -> None:
    op.drop_column("flows", "vertical_key")
    op.drop_column("tenants", "active_flow_id")
    op.drop_column("tenants", "flow_mode")

