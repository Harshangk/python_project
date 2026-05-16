"""create_mstmenu_maprolemenu

Revision ID: 13ef763611dc
Revises: 8a5810b0054e
Create Date: 2026-03-20 11:44:43.480491

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "13ef763611dc"
down_revision: Union[str, Sequence[str], None] = "8a5810b0054e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "mstmenu",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("menu_name", sa.String(length=50), nullable=False),
        sa.Column("menu_icon", sa.String(length=50), nullable=True),
        sa.Column("menu_path", sa.String(length=255), nullable=True),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("order_no", sa.Integer(), nullable=False),
        sa.Column(
            "badge_count", sa.Integer(), server_default=sa.text("0"), nullable=False
        ),
        sa.Column(
            "created_at", sa.DateTime(), server_default=text("now()"), nullable=False
        ),
        sa.Column(
            "is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
        sa.Column(
            "is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_mstmenu")),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["mstmenu.id"],
            name=op.f("fk_mstmenu_parent_id_mstmenu"),
        ),
    )

    op.create_table(
        "maprolemenu",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("menu_id", sa.Integer(), nullable=False),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_maprolemenu")),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["mstrole.id"],
            name=op.f("fk_maprolemenu_role_id_mstrole"),
        ),
        sa.ForeignKeyConstraint(
            ["menu_id"],
            ["mstmenu.id"],
            name=op.f("fk_maprolemenu_menu_id_mstmenu"),
        ),
        sa.UniqueConstraint(
            "role_id", "menu_id", name=op.f("uq_maprolemenu_role_id_menu_id")
        ),
    )

    op.create_index("idx_maprolemenu_role_id", "maprolemenu", ["role_id"])
    op.create_index("idx_maprolemenu_menu_id", "maprolemenu", ["menu_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("maprolemenu")
    op.drop_table("mstmenu")
