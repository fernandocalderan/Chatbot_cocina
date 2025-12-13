"""add roles enum values and normalize"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0013_add_roles_enum_super_admin"
down_revision = "0012_add_ia_enabled_and_usage_fields"
branch_labels = None
depends_on = None


def upgrade():
    # Normalizar roles existentes a mayúsculas conocidas
    op.execute(
        """
        UPDATE users
        SET role = UPPER(role)
        WHERE role IS NOT NULL
        """
    )
    # Forzar valor por defecto a ADMIN en mayúsculas
    op.alter_column(
        "users",
        "role",
        server_default="ADMIN",
        existing_type=sa.String(length=50),
        nullable=False,
    )


def downgrade():
    op.alter_column(
        "users",
        "role",
        server_default="admin",
        existing_type=sa.String(length=50),
        nullable=False,
    )
