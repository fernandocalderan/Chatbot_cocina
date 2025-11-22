"""ai prompts and ai cost"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

# revision identifiers, used by Alembic.
revision: str = "0002_ai_prompts"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("tenants", sa.Column("ai_cost", sa.Float(), nullable=False, server_default="0"))
    op.add_column("tenants", sa.Column("ai_monthly_limit", sa.Float(), nullable=False, server_default="100"))

    op.create_table(
        "ai_prompts",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", pg.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column("prompt_text", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "name", "version", name="uq_prompt_tenant_name_version"),
    )


def downgrade() -> None:
    op.drop_table("ai_prompts")
    op.drop_column("tenants", "ai_monthly_limit")
    op.drop_column("tenants", "ai_cost")
