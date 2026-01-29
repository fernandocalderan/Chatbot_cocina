"""add subflows and routing fields

Revision ID: 0022_add_subflows_and_routing_fields
Revises: 0021_add_tenant_flow_overrides
Create Date: 2026-01-29
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0022_add_subflows_and_routing_fields"
down_revision = "0021_add_tenant_flow_overrides"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("flows", sa.Column("parent_flow_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("flows", sa.Column("subflow_key", sa.String(length=128), nullable=True))
    op.add_column("flows", sa.Column("trigger_keywords", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column(
        "flows",
        sa.Column(
            "trigger_priority",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("5"),
        ),
    )
    op.add_column(
        "flows",
        sa.Column(
            "trigger_threshold",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
        ),
    )
    op.add_column(
        "flows",
        sa.Column(
            "archived",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    op.create_index(
        "ix_flows_vertical_scope_kind",
        "flows",
        ["vertical_key", "scope_key", "flow_kind"],
    )
    op.create_index(
        "ix_flows_parent_flow_id",
        "flows",
        ["parent_flow_id"],
    )
    op.create_index(
        "uq_flows_subflow_key_per_parent_owner",
        "flows",
        ["owner_type", "owner_id", "parent_flow_id", "subflow_key"],
        unique=True,
        postgresql_where=sa.text("archived = false"),
    )


def downgrade() -> None:
    op.drop_index("uq_flows_subflow_key_per_parent_owner", table_name="flows")
    op.drop_index("ix_flows_parent_flow_id", table_name="flows")
    op.drop_index("ix_flows_vertical_scope_kind", table_name="flows")

    op.drop_column("flows", "archived")
    op.drop_column("flows", "trigger_threshold")
    op.drop_column("flows", "trigger_priority")
    op.drop_column("flows", "trigger_keywords")
    op.drop_column("flows", "subflow_key")
    op.drop_column("flows", "parent_flow_id")
