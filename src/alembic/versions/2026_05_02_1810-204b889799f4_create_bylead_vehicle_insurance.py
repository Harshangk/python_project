"""create bylead vehicle insurance

Revision ID: 204b889799f4
Revises: d4d7197f3a3f
Create Date: 2026-05-02 18:10:40.123378

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "204b889799f4"
down_revision: Union[str, Sequence[str], None] = "d4d7197f3a3f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tblbuylead_vehicle_insurance",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("buylead_id", sa.Integer(), nullable=False),
        sa.Column("insurance_type", sa.String(6), nullable=False),
        sa.Column("cp_zd_company", sa.String(255), nullable=True),
        sa.Column("tp_company", sa.String(255), nullable=True),
        sa.Column("cp_zd_date", sa.DateTime(), nullable=True),
        sa.Column("tp_date", sa.DateTime(), nullable=True),
        sa.Column(
            "idv", sa.Numeric(12, 2), server_default=text("0.00"), nullable=False
        ),
        sa.Column(
            "ncb", sa.Numeric(12, 2), server_default=text("0.00"), nullable=False
        ),
        sa.Column(
            "premium", sa.Numeric(12, 2), server_default=text("0.00"), nullable=False
        ),
        sa.Column(
            "created_at", sa.DateTime(), server_default=text("now()"), nullable=False
        ),
        sa.Column("created_by", sa.String(50), nullable=False),
        sa.Column("modified_at", sa.DateTime(), nullable=True),
        sa.Column("modified_by", sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(
            ["buylead_id"],
            ["tblbuylead.id"],
            name=op.f("fk_tblbuylead_vehicle_insurance_buylead_id_tblbuylead"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tblbuylead_vehicle_insurance")),
        sa.UniqueConstraint(
            "buylead_id", name=op.f("uq_tblbuylead_vehicle_insurance_buylead_id")
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("tblbuylead_vehicle_insurance")
