"""create_mstrole_table

Revision ID: c05321f8cacf
Revises: cfe64e6c166a
Create Date: 2026-03-14 10:24:02.947058

"""

from datetime import datetime
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import func

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c05321f8cacf"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "mstrole",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("role", sa.String(length=15), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=func.now(), nullable=True
        ),
        sa.Column("created_by", sa.String(50), nullable=True),
        sa.Column("modified_at", sa.DateTime(), nullable=True),
        sa.Column("modified_by", sa.String(50), nullable=True),
        sa.Column(
            "is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
        sa.Column(
            "is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_mstrole")),
        sa.UniqueConstraint("role", name=op.f("uq_mstrole_role")),
    )

    op.execute("""INSERT INTO mstrole(role) VALUES('Super Admin')""")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("mstrole")
