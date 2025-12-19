"""schema alignment for runtime/models

Revision ID: 0019_schema_alignment
Revises: 0018_merge_heads_customer_code_and_verticals
Create Date: 2025-12-19
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg


revision = "0019_schema_alignment"
down_revision = "0018_merge_heads_customer_code_and_verticals"
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


def _fkset(insp: sa.Inspector, table: str) -> set[tuple[str, str, str]]:
    """
    Returns {(constrained_column, referred_table, referred_column)}.
    """
    out: set[tuple[str, str, str]] = set()
    try:
        for fk in insp.get_foreign_keys(table):
            cols = fk.get("constrained_columns") or []
            ref_table = fk.get("referred_table")
            ref_cols = fk.get("referred_columns") or []
            if len(cols) == 1 and ref_table and len(ref_cols) == 1:
                out.add((str(cols[0]), str(ref_table), str(ref_cols[0])))
    except Exception:
        return out
    return out


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # ----------------------------
    # conversation_templates
    # ----------------------------
    if not _has_table(insp, "conversation_templates"):
        op.create_table(
            "conversation_templates",
            sa.Column(
                "id",
                pg.UUID(as_uuid=True),
                primary_key=True,
                server_default=sa.text("gen_random_uuid()"),
            ),
            sa.Column(
                "tenant_id",
                pg.UUID(as_uuid=True),
                sa.ForeignKey("tenants.id", ondelete="CASCADE"),
                nullable=True,
            ),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column(
                "schema_json",
                pg.JSONB,
                nullable=False,
                server_default=sa.text("'{}'::jsonb"),
            ),
            sa.Column(
                "is_default",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
                onupdate=sa.func.now(),
            ),
        )
        op.create_index(
            "ix_conversation_templates_tenant_created",
            "conversation_templates",
            ["tenant_id", "created_at"],
            unique=False,
        )
        op.create_index(
            "ix_conversation_templates_default",
            "conversation_templates",
            ["tenant_id", "is_default"],
            unique=False,
        )

    # FK tenants.default_template_id -> conversation_templates.id (modelo ORM lo espera)
    tenant_fks = _fkset(insp, "tenants")
    if ("default_template_id", "conversation_templates", "id") not in tenant_fks:
        try:
            op.create_foreign_key(
                "fk_tenants_default_template",
                "tenants",
                "conversation_templates",
                ["default_template_id"],
                ["id"],
                ondelete="SET NULL",
            )
        except Exception:
            pass

    # ----------------------------
    # tenants: columnas usadas por runtime/panel
    # ----------------------------
    tenant_cols = _colset(insp, "tenants")

    def add_tenant_col(name: str, column: sa.Column) -> None:
        if name in tenant_cols:
            return
        op.add_column("tenants", column)
        tenant_cols.add(name)

    add_tenant_col(
        "use_ia",
        sa.Column(
            "use_ia",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    add_tenant_col(
        "google_calendar_connected",
        sa.Column(
            "google_calendar_connected",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    add_tenant_col("google_refresh_token", sa.Column("google_refresh_token", sa.String(length=1024), nullable=True))
    add_tenant_col("google_calendar_id", sa.Column("google_calendar_id", sa.String(length=255), nullable=True))
    add_tenant_col(
        "microsoft_calendar_connected",
        sa.Column(
            "microsoft_calendar_connected",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    add_tenant_col("microsoft_refresh_token", sa.Column("microsoft_refresh_token", sa.String(length=1024), nullable=True))
    add_tenant_col("microsoft_calendar_id", sa.Column("microsoft_calendar_id", sa.String(length=255), nullable=True))
    add_tenant_col("usage_limit_monthly", sa.Column("usage_limit_monthly", sa.Float(), nullable=True))

    # ia_plan: el modelo usa Enum name="ia_plan_enum", pero migraciones previas lo dejaron como plan_enum.
    # Alinearlo a `ia_plan_enum` y hacerlo NOT NULL con DEFAULT.
    try:
        if getattr(bind.dialect, "name", "") == "postgresql":
            bind.execute(
                sa.text(
                    """
                    DO $$
                    BEGIN
                      IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'ia_plan_enum') THEN
                        CREATE TYPE ia_plan_enum AS ENUM ('BASE','PRO','ELITE');
                      END IF;
                    END$$;
                    """
                )
            )
            bind.execute(sa.text("UPDATE tenants SET ia_plan='BASE' WHERE ia_plan IS NULL"))
            bind.execute(sa.text("ALTER TABLE tenants ALTER COLUMN ia_plan DROP DEFAULT"))
            bind.execute(
                sa.text(
                    "ALTER TABLE tenants ALTER COLUMN ia_plan TYPE ia_plan_enum USING ia_plan::text::ia_plan_enum"
                )
            )
            bind.execute(sa.text("ALTER TABLE tenants ALTER COLUMN ia_plan SET DEFAULT 'BASE'"))
            bind.execute(sa.text("ALTER TABLE tenants ALTER COLUMN ia_plan SET NOT NULL"))
    except Exception:
        pass

    # ----------------------------
    # leads: columnas usadas por widget/CRM
    # ----------------------------
    leads_cols = _colset(insp, "leads")

    def add_lead_col(name: str, column: sa.Column) -> None:
        if name in leads_cols:
            return
        op.add_column("leads", column)
        leads_cols.add(name)

    add_lead_col(
        "owner_id",
        sa.Column(
            "owner_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    add_lead_col("source", sa.Column("source", sa.String(length=100), nullable=True))
    add_lead_col("lost_reason", sa.Column("lost_reason", sa.String(length=255), nullable=True))
    add_lead_col("expected_value", sa.Column("expected_value", sa.Numeric(precision=12, scale=2), nullable=True))
    add_lead_col("closed_at", sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True))

    # ----------------------------
    # appointments: columnas usadas por agenda providers
    # ----------------------------
    appt_cols = _colset(insp, "appointments")

    def add_appt_col(name: str, column: sa.Column) -> None:
        if name in appt_cols:
            return
        op.add_column("appointments", column)
        appt_cols.add(name)

    add_appt_col("reminder_status", sa.Column("reminder_status", sa.String(length=30), nullable=True))
    add_appt_col("external_event_id_google", sa.Column("external_event_id_google", sa.String(length=255), nullable=True))
    add_appt_col(
        "external_event_id_microsoft", sa.Column("external_event_id_microsoft", sa.String(length=255), nullable=True)
    )

    # ----------------------------
    # tables missing from initial migrations but present in models
    # ----------------------------
    if not _has_table(insp, "activities"):
        op.create_table(
            "activities",
            sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column("tenant_id", pg.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
            sa.Column("lead_id", pg.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
            sa.Column("user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("type", sa.String(length=30), nullable=False),
            sa.Column("content", sa.String(length=500), nullable=False),
            sa.Column("meta", pg.JSONB, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_activities_lead_created", "activities", ["lead_id", "created_at"], unique=False)

    if not _has_table(insp, "tasks"):
        op.create_table(
            "tasks",
            sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column("tenant_id", pg.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
            sa.Column("lead_id", pg.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="SET NULL"), nullable=True),
            sa.Column("owner_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=30), nullable=False, server_default="pendiente"),
            sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("priority", sa.String(length=10), nullable=False, server_default="media"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        )
        op.create_index("ix_tasks_tenant_owner_status", "tasks", ["tenant_id", "owner_id", "status"], unique=False)


def downgrade() -> None:
    # Downgrade conservador: no eliminamos columnas/tipos añadidos porque pueden contener datos en producción.
    # Solo eliminamos tablas creadas si existieran.
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if _has_table(insp, "tasks"):
        try:
            op.drop_index("ix_tasks_tenant_owner_status", table_name="tasks")
        except Exception:
            pass
        op.drop_table("tasks")

    if _has_table(insp, "activities"):
        try:
            op.drop_index("ix_activities_lead_created", table_name="activities")
        except Exception:
            pass
        op.drop_table("activities")

    if _has_table(insp, "conversation_templates"):
        try:
            op.drop_index("ix_conversation_templates_default", table_name="conversation_templates")
            op.drop_index("ix_conversation_templates_tenant_created", table_name="conversation_templates")
        except Exception:
            pass
        op.drop_table("conversation_templates")
