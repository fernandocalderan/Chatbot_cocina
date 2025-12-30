"""flow_generations and kb_chunks (pgvector)

Revision ID: 0008_flow_generations_and_kb_chunks
Revises: 0007_key_state
Create Date: 2025-12-29
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from pgvector.sqlalchemy import Vector


revision: str = "0008_flow_generations_and_kb_chunks"
down_revision: Union[str, None] = "0007_key_state"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Required by kb_chunks.embedding
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    op.create_table(
        "flow_generations",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", pg.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="queued"),
        sa.Column("source", sa.String(30), nullable=True),
        sa.Column("requested_by_user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("scopes", pg.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("languages", pg.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("selected_file_ids", pg.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("model", sa.String(100), nullable=True),
        sa.Column("tokens_in", sa.Integer, nullable=False, server_default="0"),
        sa.Column("tokens_out", sa.Integer, nullable=False, server_default="0"),
        sa.Column("cost_eur", sa.Numeric(precision=12, scale=6), nullable=False, server_default="0"),
        sa.Column("result_flow_id", pg.UUID(as_uuid=True), sa.ForeignKey("flows.id", ondelete="SET NULL"), nullable=True),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("meta", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_flow_generations_tenant_created", "flow_generations", ["tenant_id", "created_at"])
    op.create_index("ix_flow_generations_tenant_status", "flow_generations", ["tenant_id", "status"])

    op.create_table(
        "kb_chunks",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", pg.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("file_id", pg.UUID(as_uuid=True), sa.ForeignKey("files.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_idx", sa.Integer, nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("embedding", Vector(1536), nullable=False),
        sa.Column("meta", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_kb_chunks_tenant_file", "kb_chunks", ["tenant_id", "file_id"])
    op.create_index("ix_kb_chunks_tenant_created", "kb_chunks", ["tenant_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_kb_chunks_tenant_created", table_name="kb_chunks")
    op.drop_index("ix_kb_chunks_tenant_file", table_name="kb_chunks")
    op.drop_table("kb_chunks")

    op.drop_index("ix_flow_generations_tenant_status", table_name="flow_generations")
    op.drop_index("ix_flow_generations_tenant_created", table_name="flow_generations")
    op.drop_table("flow_generations")

    # Keep extension installed (best-effort). Uncomment if you want strict cleanup:
    # op.execute("DROP EXTENSION IF EXISTS vector;")

