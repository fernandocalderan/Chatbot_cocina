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
    conn = op.get_bind()
    insp = sa.inspect(conn)
    cols = {c["name"] for c in insp.get_columns("tenants")}

    # 1) add nullable column (idempotente)
    if "customer_code" not in cols:
        op.add_column(
            "tenants",
            sa.Column("customer_code", sa.String(length=20), nullable=True),
        )

    # 2) backfill sequential codes solo para NULLs
    tenants = list(
        conn.execute(
            sa.text("SELECT id FROM tenants WHERE customer_code IS NULL ORDER BY created_at ASC, id ASC")
        )
    )
    if tenants:
        # Continuar desde el máximo existente si lo hay.
        last = conn.execute(sa.text("SELECT max(customer_code) FROM tenants")).scalar()
        seq = 0
        if last:
            try:
                seq = int(str(last).split("-")[-1])
            except Exception:
                seq = 0
        for row in tenants:
            seq += 1
            code = f"OPN-{seq:06d}"
            conn.execute(
                sa.text("UPDATE tenants SET customer_code=:code WHERE id=:id AND customer_code IS NULL"),
                {"code": code, "id": row.id},
            )

    # 3) set NOT NULL + unique index (idempotente)
    try:
        op.alter_column("tenants", "customer_code", nullable=False)
    except Exception:
        pass
    try:
        conn.execute(sa.text("CREATE UNIQUE INDEX IF NOT EXISTS ix_tenants_customer_code ON tenants (customer_code)"))
    except Exception:
        pass


def downgrade():
    conn = op.get_bind()
    try:
        conn.execute(sa.text("DROP INDEX IF EXISTS ix_tenants_customer_code"))
    except Exception:
        pass
    insp = sa.inspect(conn)
    cols = {c["name"] for c in insp.get_columns("tenants")}
    if "customer_code" in cols:
        op.drop_column("tenants", "customer_code")
