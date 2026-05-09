"""create evaluation parameters

Revision ID: 06f2fac9d799
Revises: 3d4dd810c76e
Create Date: 2026-05-09 15:22:02.482999

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "06f2fac9d799"
down_revision: Union[str, Sequence[str], None] = "3d4dd810c76e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "mstpart",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("part_name", sa.String(length=50), nullable=False),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_mstpart")),
        sa.UniqueConstraint("part_name", name=op.f("uq_mstpart_part_name")),
    )

    op.create_table(
        "mstsubpart",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("part_id", sa.Integer(), nullable=False),
        sa.Column("subpart_name", sa.String(length=50), nullable=False),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_mstsubpart")),
        sa.ForeignKeyConstraint(
            ["part_id"],
            ["mstpart.id"],
            name=op.f("fk_mstsubpart_part_id_mstpart"),
        ),
    )
    op.create_index("idx_mstsubpart_part_id", "mstsubpart", ["part_id"])

    op.create_table(
        "mstsubpartstatus",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("subpart_id", sa.Integer(), nullable=False),
        sa.Column("subpart_status", sa.String(length=50), nullable=False),
        sa.Column(
            "is_default", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_mstsubpartstatus")),
        sa.ForeignKeyConstraint(
            ["subpart_id"],
            ["mstsubpart.id"],
            name=op.f("fk_mstsubpartstatus_subpart_id_mstsubpartstatus"),
        ),
    )
    op.create_index(
        "idx_mstsubpartstatus_subpart_id", "mstsubpartstatus", ["subpart_id"]
    )

    op.create_table(
        "mstsubpartsubstatus",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("subpartstatus_id", sa.Integer(), nullable=False),
        sa.Column("subpart_sub_status", sa.String(length=50), nullable=False),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_mstsubpartsubstatus")),
        sa.ForeignKeyConstraint(
            ["subpartstatus_id"],
            ["mstsubpartstatus.id"],
            name=op.f("fk_mstsubpartsubstatus_subpartstatus_id_mstsubpartsubstatus"),
        ),
    )
    op.create_index(
        "idx_mstsubpartsubstatus_subpartstatus_id",
        "mstsubpartsubstatus",
        ["subpartstatus_id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("mstsubpartsubstatus")
    op.drop_table("mstsubpartstatus")
    op.drop_table("mstsubpart")
    op.drop_table("mstpart")


# INSERT INTO mstpart (part_name,created_by) VALUES ('Accident','Harshang') # noqa
# INSERT INTO mstpart (part_name,created_by) VALUES ('Bumper','Harshang') # noqa
# INSERT INTO mstpart (part_name,created_by) VALUES ('Bonet/Hood','Harshang') # noqa

# INSERT INTO mstsubpart (part_id,subpart_name,created_by) VALUES (1,'Major','Harshang') # noqa
# INSERT INTO mstsubpart (part_id,subpart_name,created_by) VALUES (1,'Minor','Harshang') # noqa
# INSERT INTO mstsubpart (part_id,subpart_name,created_by) VALUES (2,'Front','Harshang') # noqa
# INSERT INTO mstsubpart (part_id,subpart_name,created_by) VALUES (2,'Rear','Harshang') # noqa
# INSERT INTO mstsubpart (part_id,subpart_name,created_by) VALUES (3,'N/A','Harshang') # noqa

# INSERT INTO mstsubpartstatus (subpart_id,subpart_status,is_default,created_by) VALUES (1,'No',true,'Harshang') # noqa
# INSERT INTO mstsubpartstatus (subpart_id,subpart_status,is_default,created_by) VALUES (1,'Yes',false,'Harshang') # noqa
# INSERT INTO mstsubpartstatus (subpart_id,subpart_status,is_default,created_by) VALUES (2,'No',true,'Harshang') # noqa
# INSERT INTO mstsubpartstatus (subpart_id,subpart_status,is_default,created_by) VALUES (2,'Yes',false,'Harshang') # noqa
# INSERT INTO mstsubpartstatus (subpart_id,subpart_status,is_default,created_by) VALUES (3,'OK',true,'Harshang') # noqa
# INSERT INTO mstsubpartstatus (subpart_id,subpart_status,is_default,created_by) VALUES (3,'Not OK',false,'Harshang') # noqa
# INSERT INTO mstsubpartstatus (subpart_id,subpart_status,is_default,created_by) VALUES (4,'OK',true,'Harshang') # noqa
# INSERT INTO mstsubpartstatus (subpart_id,subpart_status,is_default,created_by) VALUES (4,'Not OK',false,'Harshang') # noqa
# INSERT INTO mstsubpartstatus (subpart_id,subpart_status,is_default,created_by) VALUES (5,'OK',true,'Harshang') # noqa
# INSERT INTO mstsubpartstatus (subpart_id,subpart_status,is_default,created_by) VALUES (5,'Not OK',false,'Harshang') # noqa

# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (2,'Apron','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (2,'Pillars','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (2,'Chais repair','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (2,'Body cell','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (4,'Door change','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (4,'Bonet change','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (4,'Dicky change','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (4,'Body panel repair','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (6,'Repainted','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (6,'Repaired','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (6,'Replaced','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (6,'Scratched','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (6,'Damaged','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (6,'Grill damaged','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (6,'Dented','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (6,'Touching','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (8,'Repainted','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (8,'Repaired','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (8,'Replaced','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (8,'Scratched','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (8,'Damaged','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (8,'Dented','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (8,'Touching','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (10,'Repainted','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (10,'Repaired','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (10,'Replaced','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (10,'Scratched','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (10,'Damaged','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (10,'Dented','Harshang') # noqa
# INSERT INTO mstsubpartsubstatus (subpartstatus_id,subpart_sub_status,created_by) VALUES (10,'Rusted','Harshang') # noqa
