"""add scopes table and flow grouping fields

Revision ID: 0020_add_scopes_and_flow_fields
Revises: 0019_schema_alignment
Create Date: 2026-01-29
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg


revision = "0020_add_scopes_and_flow_fields"
down_revision = "0019_schema_alignment"
branch_labels = None
depends_on = None


def _has_table(insp: sa.Inspector, table: str) -> bool:
    try:
        return table in set(insp.get_table_names())
    except Exception:
        return False


def _colset(insp: sa.Inspector, table: str) -> set[str]:
    try:
        return {c["name"] for c in insp.get_columns(table)}
    except Exception:
        return set()


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if not _has_table(insp, "scopes"):
        op.create_table(
            "scopes",
            sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
            sa.Column("vertical_key", sa.String(length=64), nullable=False),
            sa.Column("scope_key", sa.String(length=64), nullable=False),
            sa.Column("display_name", sa.String(length=255), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
            sa.UniqueConstraint("vertical_key", "scope_key", name="uq_scopes_vertical_scope"),
        )
        op.create_index("ix_scopes_vertical", "scopes", ["vertical_key"], unique=False)

    flow_cols = _colset(insp, "flows")
    if "scope_key" not in flow_cols:
        op.add_column("flows", sa.Column("scope_key", sa.String(length=64), nullable=True))
    if "owner_type" not in flow_cols:
        op.add_column(
            "flows",
            sa.Column("owner_type", sa.String(length=32), nullable=False, server_default="TENANT"),
        )
    if "owner_id" not in flow_cols:
        op.add_column("flows", sa.Column("owner_id", pg.UUID(as_uuid=True), nullable=True))
    if "flow_kind" not in flow_cols:
        op.add_column(
            "flows",
            sa.Column("flow_kind", sa.String(length=32), nullable=False, server_default="base"),
        )

    try:
        op.alter_column("flows", "tenant_id", existing_type=pg.UUID(as_uuid=True), nullable=True)
    except Exception:
        pass

    # Backfill grouping fields for existing rows
    try:
        bind.execute(sa.text("UPDATE flows SET owner_type='TENANT' WHERE owner_type IS NULL"))
        bind.execute(sa.text("UPDATE flows SET flow_kind='base' WHERE flow_kind IS NULL"))
        bind.execute(sa.text("UPDATE flows SET owner_id=tenant_id WHERE owner_id IS NULL AND owner_type='TENANT'"))
    except Exception:
        pass


def downgrade() -> None:
    # No downgrade: data model expansion
    pass
