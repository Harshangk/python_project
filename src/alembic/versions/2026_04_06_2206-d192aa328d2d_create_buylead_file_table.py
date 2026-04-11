"""create buylead_file table

Revision ID: d192aa328d2d
Revises: 7bdcb8e46ebd
Create Date: 2026-04-06 22:06:51.830983

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d192aa328d2d"
down_revision: Union[str, Sequence[str], None] = "7bdcb8e46ebd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tblbuylead_file",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("s3_key", sa.Text(), nullable=False),
        sa.Column("file_status", sa.String(length=10), nullable=False),
        sa.Column("file_uuid", sa.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "processed_records", sa.Integer(), server_default=text("0"), nullable=False
        ),
        sa.Column(
            "error_records", sa.Integer(), server_default=text("0"), nullable=False
        ),
        sa.Column(
            "created_at", sa.DateTime(), server_default=text("now()"), nullable=False
        ),
        sa.Column("created_by", sa.String(50), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tblbuylead_file")),
        sa.UniqueConstraint("file_uuid", name=op.f("uq_tblbuylead_file_file_uuid")),
    )

    op.create_index(
        "idx_tblbuylead_file_file_uuid",
        "tblbuylead_file",
        ["file_uuid"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("tblbuylead_file")
