"""magic login tokens and must_set_password

Revision ID: 0011_magic_login_tokens
Revises: 0010_add_tenant_ia_limit
Create Date: 2025-12-15 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg


revision = "0011_magic_login_tokens"
down_revision = "0010_add_tenant_ia_limit"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # Idempotente: algunos entornos ya tienen estas columnas/tablas aunque el alembic_version no lo refleje.
    user_cols = {c["name"] for c in insp.get_columns("users")}
    if "must_set_password" not in user_cols:
        op.add_column(
            "users",
            sa.Column(
                "must_set_password",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("true"),
            ),
        )
    try:
        op.alter_column("users", "status", server_default="ACTIVE")
        op.execute("UPDATE users SET status = upper(status)")
    except Exception:
        pass

    if "login_tokens" not in set(insp.get_table_names()):
        op.create_table(
            "login_tokens",
            sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column("user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("token_hash", sa.String(length=128), nullable=False),
            sa.Column("jti", sa.String(length=64), nullable=True),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint("token_hash", name="uq_login_token_hash"),
        )


def downgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if "login_tokens" in set(insp.get_table_names()):
        op.drop_table("login_tokens")
    user_cols = {c["name"] for c in insp.get_columns("users")}
    if "must_set_password" in user_cols:
        op.drop_column("users", "must_set_password")
    try:
        op.alter_column("users", "status", server_default="active")
    except Exception:
        pass
