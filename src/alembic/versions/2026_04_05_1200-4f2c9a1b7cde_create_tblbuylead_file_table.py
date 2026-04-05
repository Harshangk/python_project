"""create_tblbuylead_file_table

Revision ID: 4f2c9a1b7cde
Revises: 7bdcb8e46ebd
Create Date: 2026-04-05 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4f2c9a1b7cde"
down_revision: Union[str, Sequence[str], None] = "7bdcb8e46ebd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tblbuylead_file",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("s3_key", sa.String(length=500), nullable=False),
        sa.Column("file_type", sa.String(length=50), nullable=False),
        sa.Column("file_uuid", sa.UUID(as_uuid=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tblbuylead_file")),
    )

    op.create_index(
        "idx_tblbuylead_file_file_type",
        "tblbuylead_file",
        ["file_type"],
    )


def downgrade() -> None:
    op.drop_index("idx_tblbuylead_file_file_type", table_name="tblbuylead_file")
    op.drop_table("tblbuylead_file")
