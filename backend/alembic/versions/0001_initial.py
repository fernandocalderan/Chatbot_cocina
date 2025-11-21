"""initial schema"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')

    op.create_table(
        "tenants",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("contact_email", sa.String(length=320), nullable=True),
        sa.Column("plan", sa.String(length=50), nullable=False, server_default="Base"),
        sa.Column("flags_ia", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("branding", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("idioma_default", sa.String(length=10), nullable=False, server_default="es"),
        sa.Column("timezone", sa.String(length=64), nullable=False, server_default="Europe/Madrid"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )
    op.create_index("ix_tenants_name", "tenants", ["name"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", pg.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="admin"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column("mfa_enabled", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.UniqueConstraint("tenant_id", "email", name="uq_user_email_tenant"),
    )

    op.create_table(
        "flows",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", pg.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column("schema_json", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("estado", sa.String(length=30), nullable=False, server_default="draft"),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rollback_to_version", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.UniqueConstraint("tenant_id", "version", name="uq_flow_version_per_tenant"),
    )

    op.create_table(
        "sessions",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", pg.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("external_user_id", sa.String(length=128), nullable=True),
        sa.Column("canal", sa.String(length=20), nullable=False, server_default="web"),
        sa.Column("idioma_detectado", sa.String(length=10), nullable=True),
        sa.Column("state", sa.String(length=50), nullable=True),
        sa.Column("variables_json", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("last_block_id", sa.String(length=100), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )
    op.create_index("ix_sessions_tenant_user", "sessions", ["tenant_id", "external_user_id"], unique=False)

    op.create_table(
        "leads",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", pg.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("session_id", pg.UUID(as_uuid=True), sa.ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("origen", sa.String(length=50), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="nuevo"),
        sa.Column("score", sa.Integer, nullable=True),
        sa.Column("score_breakdown_json", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("metadata", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("idioma", sa.String(length=10), nullable=True),
        sa.Column("timezone", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )
    op.create_index("ix_leads_tenant_created", "leads", ["tenant_id", "created_at"], unique=False)
    op.create_index("ix_leads_status", "leads", ["status"], unique=False)

    op.create_table(
        "appointments",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", pg.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lead_id", pg.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="SET NULL"), nullable=True),
        sa.Column("slot_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("slot_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("estado", sa.String(length=30), nullable=False, server_default="pending"),
        sa.Column("origen", sa.String(length=30), nullable=True),
        sa.Column("notas", sa.Text, nullable=True),
        sa.Column("reminder_status", sa.String(length=30), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )
    op.create_index("ix_appointments_tenant_slot", "appointments", ["tenant_id", "slot_start"], unique=False)

    op.create_table(
        "configs",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", pg.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tipo", sa.String(length=50), nullable=False),
        sa.Column("payload_json", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )
    op.create_index("ix_configs_tenant_tipo", "configs", ["tenant_id", "tipo"], unique=False)

    op.create_table(
        "messages",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("tenant_id", pg.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "session_id", pg.UUID(as_uuid=True), sa.ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("block_id", sa.String(length=100), nullable=True),
        sa.Column("ai_meta", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("attachments", pg.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_messages_session_created", "messages", ["session_id", "created_at"], unique=False)

    op.create_table(
        "files",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", pg.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lead_id", pg.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="SET NULL"), nullable=True),
        sa.Column("s3_key", sa.String(length=255), nullable=False),
        sa.Column("tipo", sa.String(length=30), nullable=True),
        sa.Column("meta", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("s3_key", name="uq_files_s3_key"),
    )
    op.create_index("ix_files_tenant_created", "files", ["tenant_id", "created_at"], unique=False)

    op.create_table(
        "audits",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("tenant_id", pg.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("entity", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("actor", sa.String(length=100), nullable=True),
        sa.Column("metadata", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_audits_tenant_created", "audits", ["tenant_id", "created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_audits_tenant_created", table_name="audits")
    op.drop_table("audits")

    op.drop_index("ix_files_tenant_created", table_name="files")
    op.drop_table("files")

    op.drop_index("ix_messages_session_created", table_name="messages")
    op.drop_table("messages")

    op.drop_index("ix_configs_tenant_tipo", table_name="configs")
    op.drop_table("configs")

    op.drop_index("ix_appointments_tenant_slot", table_name="appointments")
    op.drop_table("appointments")

    op.drop_index("ix_leads_status", table_name="leads")
    op.drop_index("ix_leads_tenant_created", table_name="leads")
    op.drop_table("leads")

    op.drop_index("ix_sessions_tenant_user", table_name="sessions")
    op.drop_table("sessions")

    op.drop_table("flows")
    op.drop_table("users")

    op.drop_index("ix_tenants_name", table_name="tenants")
    op.drop_table("tenants")
