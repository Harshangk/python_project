"""create preprice model

Revision ID: 6e15a14737d2
Revises: ec5424b0cccf
Create Date: 2026-05-30 11:24:26.580806

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6e15a14737d2"
down_revision: Union[str, Sequence[str], None] = "ec5424b0cccf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tblbuylead_preprice",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("buylead_id", sa.Integer(), nullable=False),
        sa.Column(
            "pre_price",
            sa.Numeric(12, 2),
            server_default=text("0.00"),
            nullable=False,
        ),
        sa.Column("remarks", sa.String(500), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=text("now()"), nullable=False
        ),
        sa.Column("created_by", sa.String(50), nullable=False),
        sa.ForeignKeyConstraint(
            ["buylead_id"],
            ["tblbuylead.id"],
            name=op.f("fk_tblbuylead_preprice_buylead_id_tblbuylead"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tblbuylead_preprice")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("tblbuylead_preprice")
