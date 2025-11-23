"""add flow and scoring tables"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

# revision identifiers, used by Alembic.
revision: str = "0003_flow_scoring_tables"
down_revision: Union[str, None] = "0002_ai_prompts_and_ai_cost"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "flow",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("data", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )

    op.create_table(
        "scoring",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("data", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("scoring")
    op.drop_table("flow")
