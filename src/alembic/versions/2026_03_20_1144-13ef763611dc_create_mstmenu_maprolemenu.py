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


# insert into mstmenu
# (menu_name,menu_icon,menu_path,parent_id, order_no)
# values
# ('Dashboard', 'LayoutDashboard', '/dashboard', NULL, 1),
# ('Leads', 'Users', NULL, NULL, 2),
# ('Buy Lead: Single', NULL, '/leads/buylead', 2, 3),
# ('Buy Lead: List', NULL, '/leads/buyleadlist', 2, 4),
# ('Untouched', NULL, '/leads/untouched', 2, 5),
# ('Smart Assignment', 'Brain', NULL, NULL, 6),
# ('Assignment Rules', NULL, '/assignment-rules', 6, 7),
# ('Budget Segmentation', NULL, '/budget', 6, 8),
# ('Make Expertise', NULL, '/expertise', 6, 9),
# ('Workload Monitor', NULL, '/workload', 6, 10),
# ('Round Robin Setup', NULL, '/round-robin', 6, 11),
# ('SLA & Escalation', NULL, '/sla', 6, 12),
# ('Automation', NULL, '/automation', 6, 13),
# ('Buy', 'ShoppingCart', NULL, NULL, 14),
# ('Untouched', NULL, '/leads/untouchedlist', 14, 15),
# ('Re-Allocation', NULL, '/leads/reallocationlist', 14, 16),
# ('Followup', NULL, '/leads/buyleadfollowuplist', 14, 17),
# ('Sale', 'TrendingUp', NULL, NULL, 18),
# ('Untouched', NULL, '/leads/untouched', 18, 19);


# insert into maprolemenu
# (role_id, menu_id,created_by)
# select 1, id, 1 from mstmenu;
