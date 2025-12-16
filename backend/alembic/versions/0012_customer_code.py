"""add customer_code to tenants

Revision ID: 0012_customer_code
Revises: 0011_magic_login_tokens
Create Date: 2025-12-16 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg


revision = "0012_customer_code"
down_revision = "0011_magic_login_tokens"
branch_labels = None
depends_on = None


def upgrade():
    # 1) add nullable column
    op.add_column(
        "tenants",
        sa.Column("customer_code", sa.String(length=20), nullable=True),
    )
    # 2) backfill sequential codes
    conn = op.get_bind()
    tenants = list(conn.execute(sa.text("SELECT id FROM tenants ORDER BY created_at ASC, id ASC")))
    counter = 1
    for row in tenants:
        code = f"OPN-{counter:06d}"
        conn.execute(
            sa.text("UPDATE tenants SET customer_code=:code WHERE id=:id"),
            {"code": code, "id": row.id},
        )
        counter += 1
    # 3) set NOT NULL + unique index
    op.alter_column("tenants", "customer_code", nullable=False)
    op.create_index("ix_tenants_customer_code", "tenants", ["customer_code"], unique=True)


def downgrade():
    op.drop_index("ix_tenants_customer_code", table_name="tenants")
    op.drop_column("tenants", "customer_code")
