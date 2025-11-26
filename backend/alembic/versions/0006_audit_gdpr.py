"""audit gdpr table

Revision ID: 0006_audit_gdpr
Revises: 0005_pii_encrypt_data
Create Date: 2025-02-09
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

# revision identifiers, used by Alembic.
revision: str = "0006_audit_gdpr"
down_revision: Union[str, None] = "0005_pii_encrypt_data"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audit_gdpr",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "tenant_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("entity", sa.String(50), nullable=False),
        sa.Column("entity_id", sa.String(64), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("actor", sa.String(100), nullable=True),
        sa.Column(
            "meta", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_audit_gdpr_tenant_created", "audit_gdpr", ["tenant_id", "created_at"]
    )


def downgrade() -> None:
    op.drop_index("ix_audit_gdpr_tenant_created", table_name="audit_gdpr")
    op.drop_table("audit_gdpr")
