"""create_mstlogin_table

Revision ID: 8a5810b0054e
Revises: c05321f8cacf
Create Date: 2026-03-14 10:24:55.251909

"""

from typing import Sequence, Union

import sqlalchemy as sa
from passlib.hash import bcrypt
from sqlalchemy import func

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8a5810b0054e"
down_revision: Union[str, Sequence[str], None] = "c05321f8cacf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "mstlogin",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("user_name", sa.String(length=50), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column("last_login", sa.DateTime(), nullable=True),
        sa.Column("login_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=func.now(), nullable=False
        ),
        sa.Column("created_by", sa.String(50), nullable=False),
        sa.Column("modified_at", sa.DateTime(), nullable=True),
        sa.Column("modified_by", sa.String(50), nullable=True),
        sa.Column("expiry_at", sa.DateTime(), nullable=True),
        sa.Column(
            "is_lock", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column(
            "is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
        sa.Column(
            "is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_mstlogin")),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["mstrole.id"],
            name=op.f("fk_mstlogin_role_id_mstrole"),
        ),
        sa.UniqueConstraint("user_name", name=op.f("uq_mstlogin_user_name")),
    )

    op.create_index("idx_mstlogin_role_id", "mstlogin", ["role_id"])
    op.create_index("idx_mstlogin_user_name", "mstlogin", ["user_name"])

    hashed_password = bcrypt.hash("0310")

    op.execute(f"""
        INSERT INTO mstlogin (role_id, user_name, password, login_at, created_at, created_by, expiry_at)
        VALUES (1, 'harshang', '{hashed_password}', now(), now(), 'harshang', now() + INTERVAL '5 years')
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("mstlogin")
