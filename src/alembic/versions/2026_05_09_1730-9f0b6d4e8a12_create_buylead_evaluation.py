"""create buylead evaluation

Revision ID: 9f0b6d4e8a12
Revises: 06f2fac9d799
Create Date: 2026-05-09 17:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9f0b6d4e8a12"
down_revision: Union[str, Sequence[str], None] = "06f2fac9d799"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tblbuylead_evaluation",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("buylead_id", sa.Integer(), nullable=False),
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
            name=op.f("fk_tblbuylead_evaluation_buylead_id_tblbuylead"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tblbuylead_evaluation")),
        sa.UniqueConstraint(
            "buylead_id", name=op.f("uq_tblbuylead_evaluation_buylead_id")
        ),
    )

    op.create_table(
        "tblbuylead_evaluation_photo",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("buylead_id", sa.Integer(), nullable=False),
        sa.Column("photo_name", sa.String(50), nullable=False),
        sa.Column("s3_key", sa.Text(), nullable=False),
        sa.Column("content_type", sa.String(100), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=text("now()"), nullable=False
        ),
        sa.Column("created_by", sa.String(50), nullable=False),
        sa.Column("modified_at", sa.DateTime(), nullable=True),
        sa.Column("modified_by", sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(
            ["buylead_id"],
            ["tblbuylead.id"],
            name=op.f("fk_tblbuylead_evaluation_photo_buylead_id_tblbuylead"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tblbuylead_evaluation_photo")),
        sa.UniqueConstraint(
            "buylead_id",
            "photo_name",
            name=op.f("uq_tblbuylead_evaluation_photo_buylead_id_photo_name"),
        ),
    )

    op.create_table(
        "tblbuylead_evaluation_parameter",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("buylead_id", sa.Integer(), nullable=False),
        sa.Column("part_id", sa.Integer(), nullable=False),
        sa.Column("subpart_id", sa.Integer(), nullable=False),
        sa.Column("subpartstatus_id", sa.Integer(), nullable=False),
        sa.Column("subpartsubstatus_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=text("now()"), nullable=False
        ),
        sa.Column("created_by", sa.String(50), nullable=False),
        sa.ForeignKeyConstraint(
            ["buylead_id"],
            ["tblbuylead.id"],
            name=op.f("fk_tblbuylead_evaluation_parameter_buylead_id_tblbuylead"),
        ),
        sa.ForeignKeyConstraint(
            ["part_id"],
            ["mstpart.id"],
            name=op.f("fk_tblbuylead_evaluation_parameter_part_id_mstpart"),
        ),
        sa.ForeignKeyConstraint(
            ["subpart_id"],
            ["mstsubpart.id"],
            name=op.f("fk_tblbuylead_evaluation_parameter_subpart_id_mstsubpart"),
        ),
        sa.ForeignKeyConstraint(
            ["subpartstatus_id"],
            ["mstsubpartstatus.id"],
            name=op.f(
                "fk_tblbuylead_evaluation_parameter_subpartstatus_id_"
                "mstsubpartstatus"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["subpartsubstatus_id"],
            ["mstsubpartsubstatus.id"],
            name=op.f(
                "fk_tblbuylead_evaluation_parameter_subpartsubstatus_id_"
                "mstsubpartsubstatus"
            ),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tblbuylead_evaluation_parameter")),
    )
    op.create_index(
        "idx_tblbuylead_evaluation_parameter_buylead_id",
        "tblbuylead_evaluation_parameter",
        ["buylead_id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "idx_tblbuylead_evaluation_parameter_buylead_id",
        table_name="tblbuylead_evaluation_parameter",
    )
    op.drop_table("tblbuylead_evaluation_parameter")
    op.drop_table("tblbuylead_evaluation_photo")
    op.drop_table("tblbuylead_evaluation")
