"""create tblbank

Revision ID: c0d626eb7bef
Revises: 204b889799f4
Create Date: 2026-05-02 18:24:54.479615

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c0d626eb7bef"
down_revision: Union[str, Sequence[str], None] = "204b889799f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tblbank",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("bank_name", sa.String(255), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=text("now()"), nullable=False
        ),
        sa.Column("created_by", sa.String(50), nullable=False),
        sa.Column("modified_at", sa.DateTime(), nullable=True),
        sa.Column("modified_by", sa.String(50), nullable=True),
        sa.Column(
            "is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
        sa.Column(
            "is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tblbank")),
        sa.UniqueConstraint("bank_name", name=op.f("uq_tblbank_bank_name")),
    )

    op.create_index("idx_tblbank_bank_name", "tblbank", ["bank_name"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("tblbank")
