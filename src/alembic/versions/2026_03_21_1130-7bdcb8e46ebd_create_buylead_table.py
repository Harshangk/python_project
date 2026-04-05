"""create_buylead_table

Revision ID: 7bdcb8e46ebd
Revises: a1d6da61fb04
Create Date: 2026-03-21 11:30:04.404832

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import func

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7bdcb8e46ebd"
down_revision: Union[str, Sequence[str], None] = "a1d6da61fb04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tblbuylead",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("branch", sa.String(50), nullable=False),
        sa.Column("mobile", sa.String(15), nullable=False),
        sa.Column("alternate_mobile", sa.String(15), nullable=True),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("mode", sa.String(25), nullable=False),
        sa.Column("broker_name", sa.String(255), nullable=True),
        sa.Column("customer_name", sa.String(255), nullable=False),
        sa.Column("make_id", sa.Integer(), nullable=False),
        sa.Column("model_id", sa.Integer(), nullable=False),
        sa.Column("variant", sa.String(255), nullable=True),
        sa.Column("color", sa.String(50), nullable=True),
        sa.Column("fuel_type", sa.String(50), nullable=False),
        sa.Column("year", sa.String(4), nullable=False),
        sa.Column("kms", sa.Integer(), nullable=False),
        sa.Column("owner", sa.String(1), nullable=False),
        sa.Column("client_offer", sa.Integer(), server_default="0", nullable=False),
        sa.Column("our_offer", sa.Integer(), server_default="0", nullable=False),
        sa.Column("status", sa.String(25), nullable=False),
        sa.Column("telecaller", sa.String(50), nullable=True),
        sa.Column("executive", sa.String(50), nullable=True),
        sa.Column("remarks", sa.String(500), nullable=False),
        sa.Column("allocated_at", sa.DateTime(), nullable=True),
        sa.Column("allocated_by", sa.String(50), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=func.now(), nullable=False
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
        sa.ForeignKeyConstraint(
            ["make_id"],
            ["mstmake.id"],
            name=op.f("fk_tblbuylead_make_id_mstmake"),
        ),
        sa.ForeignKeyConstraint(
            ["model_id"],
            ["mstmodel.id"],
            name=op.f("fk_tblbuylead_model_id_mstmodel"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tblbuylead")),
    )

    op.create_index("idx_tblbuylead_branch", "tblbuylead", ["branch"])
    op.create_index("idx_tblbuylead_mobile", "tblbuylead", ["mobile"])
    op.create_index("idx_tblbuylead_status", "tblbuylead", ["status"])
    op.create_index("idx_tblbuylead_telecaller", "tblbuylead", ["telecaller"])
    op.create_index("idx_tblbuylead_executive", "tblbuylead", ["executive"])

    op.create_table(
        "tblbuylead_address",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("buylead_id", sa.Integer(), nullable=False),
        sa.Column("address", sa.String(100), nullable=False),
        sa.Column("state", sa.String(25), nullable=False),
        sa.Column("city", sa.String(25), nullable=False),
        sa.Column("area", sa.String(25), nullable=False),
        sa.Column("pincode", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["buylead_id"],
            ["tblbuylead.id"],
            name=op.f("fk_tblbuylead_address_buylead_id_tblbuylead"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tblbuylead_address")),
        sa.UniqueConstraint(
            "buylead_id", name=op.f("uq_tblbuylead_address_buylead_id")
        ),
    )

    op.create_table(
        "tblbuylead_followup",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("buylead_id", sa.Integer(), nullable=False),
        sa.Column("stage", sa.String(25), nullable=False),
        sa.Column("disposition", sa.String(50), nullable=False),
        sa.Column("calldate", sa.DateTime(), nullable=False),
        sa.Column("preferred_time", sa.String(20), nullable=True),
        sa.Column("notes", sa.String(500), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=func.now(), nullable=False
        ),
        sa.Column("created_by", sa.String(50), nullable=False),
        sa.ForeignKeyConstraint(
            ["buylead_id"],
            ["tblbuylead.id"],
            name=op.f("fk_tblbuylead_followup_buylead_id_tblbuylead"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tblbuylead_followup")),
        sa.UniqueConstraint(
            "buylead_id", name=op.f("uq_tblbuylead_followup_buylead_id")
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("tblbuylead_followup")
    op.drop_table("tblbuylead_address")
    op.drop_table("tblbuylead")
