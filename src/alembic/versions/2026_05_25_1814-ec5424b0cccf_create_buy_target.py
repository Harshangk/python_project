"""create buy target

Revision ID: ec5424b0cccf
Revises: 1fb85130e255
Create Date: 2026-05-25 18:14:02.240504

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ec5424b0cccf"
down_revision: Union[str, Sequence[str], None] = "1fb85130e255"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tblbuylead_target",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("user_name", sa.String(50), nullable=False),
        sa.Column("month", sa.String(9), nullable=False),
        sa.Column("Year", sa.String(4), nullable=False),
        sa.Column("normal", sa.Integer(), server_default=text("0"), nullable=False),
        sa.Column("premium", sa.Integer(), server_default=text("0"), nullable=False),
        sa.Column("total", sa.Integer(), server_default=text("0"), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=text("now()"), nullable=False
        ),
        sa.Column("created_by", sa.String(50), nullable=False),
        sa.Column("modified_at", sa.DateTime(), nullable=True),
        sa.Column("modified_by", sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tblbuylead_target")),
        sa.UniqueConstraint(
            "user_name",
            "month",
            "Year",
            name=op.f("uq_tblbuylead_target_user_name_month_year"),
        ),
    )

    op.create_index(
        "idx_tblbuylead_target_user_name", "tblbuylead_target", ["user_name"]
    )
    op.create_index("idx_tblbuylead_target_month", "tblbuylead_target", ["month"])
    op.create_index("idx_tblbuylead_target_year", "tblbuylead_target", ["Year"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("tblbuylead_target")
