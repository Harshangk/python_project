"""create buylead payment

Revision ID: ae3767d367e7
Revises: d192aa328d2d
Create Date: 2026-05-02 14:51:43.306058

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ae3767d367e7"
down_revision: Union[str, Sequence[str], None] = "d192aa328d2d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tblbuylead_payment",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("buylead_id", sa.Integer(), nullable=False),
        sa.Column(
            "refurb_cost",
            sa.Numeric(12, 2),
            server_default=text("0.00"),
            nullable=False,
        ),
        sa.Column(
            "deal", sa.Numeric(12, 2), server_default=text("0.00"), nullable=False
        ),
        sa.Column(
            "service_charge",
            sa.Numeric(12, 2),
            server_default=text("0.00"),
            nullable=False,
        ),
        sa.Column(
            "tcs", sa.Numeric(12, 2), server_default=text("0.00"), nullable=False
        ),
        sa.Column(
            "gst", sa.Numeric(12, 2), server_default=text("0.00"), nullable=False
        ),
        sa.Column(
            "tax", sa.Numeric(12, 2), server_default=text("0.00"), nullable=False
        ),
        sa.Column(
            "rcd", sa.Numeric(12, 2), server_default=text("0.00"), nullable=False
        ),
        sa.Column(
            "commission", sa.Numeric(12, 2), server_default=text("0.00"), nullable=False
        ),
        sa.Column(
            "deal_with_commission",
            sa.Numeric(12, 2),
            server_default=text("0.00"),
            nullable=False,
        ),
        sa.Column(
            "deal_without_commission",
            sa.Numeric(12, 2),
            server_default=text("0.00"),
            nullable=False,
        ),
        sa.Column(
            "token", sa.Numeric(12, 2), server_default=text("0.00"), nullable=False
        ),
        sa.Column(
            "cash", sa.Numeric(12, 2), server_default=text("0.00"), nullable=False
        ),
        sa.Column(
            "loan", sa.Numeric(12, 2), server_default=text("0.00"), nullable=False
        ),
        sa.Column(
            "less", sa.Numeric(12, 2), server_default=text("0.00"), nullable=False
        ),
        sa.Column(
            "hold", sa.Numeric(12, 2), server_default=text("0.00"), nullable=False
        ),
        sa.Column(
            "ch_rtgs", sa.Numeric(12, 2), server_default=text("0.00"), nullable=False
        ),
        sa.Column(
            "total_payble",
            sa.Numeric(12, 2),
            server_default=text("0.00"),
            nullable=False,
        ),
        sa.Column("remarks", sa.String(500), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=text("now()"), nullable=False
        ),
        sa.Column("created_by", sa.String(50), nullable=False),
        sa.Column("modified_at", sa.DateTime(), nullable=True),
        sa.Column("modified_by", sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(
            ["buylead_id"],
            ["tblbuylead.id"],
            name=op.f("fk_tblbuylead_payment_buylead_id_tblbuylead"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tblbuylead_payment")),
        sa.UniqueConstraint(
            "buylead_id", name=op.f("uq_tblbuylead_payment_buylead_id")
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("tblbuylead_payment")
