"""add tenant flow overrides

Revision ID: 0021_add_tenant_flow_overrides
Revises: 0020_add_scopes_and_flow_fields
Create Date: 2026-01-29
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0021_add_tenant_flow_overrides"
down_revision = "0020_add_scopes_and_flow_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenant_flow_overrides",
        sa.Column("flow_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("base_flow_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("flows.id", ondelete="CASCADE"), nullable=False),
        sa.Column("draft_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("published", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "base_flow_id", name="uq_tenant_base_flow_override"),
    )


def downgrade() -> None:
    op.drop_table("tenant_flow_overrides")
