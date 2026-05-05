"""create bylead vehicle

Revision ID: d4d7197f3a3f
Revises: ae3767d367e7
Create Date: 2026-05-02 17:34:50.286583

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d4d7197f3a3f"
down_revision: Union[str, Sequence[str], None] = "ae3767d367e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tblbuylead_vehicle",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("buylead_id", sa.Integer(), nullable=False),
        sa.Column("registration_no", sa.String(12), nullable=False),
        sa.Column("transmission", sa.String(8), nullable=False),
        sa.Column(
            "cubic_capacity", sa.Integer(), server_default=text("0"), nullable=False
        ),
        sa.Column("push_button", sa.String(3), nullable=True),
        sa.Column("reg_month", sa.String(9), nullable=True),
        sa.Column("reg_year", sa.String(4), nullable=True),
        sa.Column("euro", sa.String(4), nullable=True),
        sa.Column("rc_book", sa.String(3), nullable=True),
        sa.Column("second_key", sa.String(3), nullable=True),
        sa.Column("hypo", sa.String(3), nullable=True),
        sa.Column("hypo_bank", sa.String(255), nullable=True),
        sa.Column("service_record", sa.String(3), nullable=True),
        sa.Column("puc", sa.String(3), nullable=True),
        sa.Column("memo", sa.String(3), nullable=True),
        sa.Column(
            "memo_amount",
            sa.Numeric(12, 2),
            server_default=text("0.00"),
            nullable=False,
        ),
        sa.Column("memo_paid", sa.String(8), nullable=True),
        sa.Column(
            "mv_tax", sa.Numeric(12, 2), server_default=text("0.00"), nullable=False
        ),
        sa.Column("rma", sa.String(8), nullable=True),
        sa.Column("taxi_private", sa.String(8), nullable=True),
        sa.Column("other_noc", sa.String(8), nullable=True),
        sa.Column("blacklist", sa.String(8), nullable=True),
        sa.Column("rto_status", sa.String(8), nullable=True),
        sa.ForeignKeyConstraint(
            ["buylead_id"],
            ["tblbuylead.id"],
            name=op.f("fk_tblbuylead_vehicle_buylead_id_tblbuylead"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tblbuylead_vehicle")),
        sa.UniqueConstraint(
            "buylead_id", name=op.f("uq_tblbuylead_vehicle_buylead_id")
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("tblbuylead_vehicle")
