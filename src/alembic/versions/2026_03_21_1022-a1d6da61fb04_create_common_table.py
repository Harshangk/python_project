"""create_common_table

Revision ID: a1d6da61fb04
Revises: 13ef763611dc
Create Date: 2026-03-21 10:22:17.786411

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1d6da61fb04"
down_revision: Union[str, Sequence[str], None] = "13ef763611dc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "mstmake",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("make", sa.String(50), nullable=False),
        sa.Column(
            "is_premium", sa.Boolean(), server_default=sa.text("false"), nullable=False
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_mstmake")),
        sa.UniqueConstraint("make", name=op.f("uq_mstmake_make")),
    )

    op.create_index("idx_mstmake_make", "mstmake", ["make"])

    op.create_table(
        "mstmodel",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("make_id", sa.Integer(), nullable=False),
        sa.Column("model", sa.String(50), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["make_id"],
            ["mstmake.id"],
            name=op.f("fk_mstmodel_make_id_mstmake"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_mstmodel")),
        sa.UniqueConstraint("make_id", "model", name=op.f("uq_mstmodel_make_id_model")),
    )

    op.create_index("idx_mstmodel_model", "mstmodel", ["model"])

    op.create_table(
        "mstbranch",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("branch", sa.String(50), nullable=False),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_mstbranch")),
        sa.UniqueConstraint("branch", name=op.f("uq_mstbranch_branch")),
    )

    op.create_index("idx_mstbranch_branch", "mstbranch", ["branch"])

    op.create_table(
        "mstsource",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("source", sa.String(50), nullable=False),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_mstsource")),
        sa.UniqueConstraint("source", name=op.f("uq_mstsource_source")),
    )

    op.create_index("idx_mstsource_source", "mstsource", ["source"])

    op.create_table(
        "mstyear",
        sa.Column("year", sa.Integer(), nullable=False, autoincrement=False),
        sa.PrimaryKeyConstraint("year", name=op.f("pk_mstyear")),
    )

    op.create_table(
        "mstbroker",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("broker", sa.String(255), nullable=False),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_mstbroker")),
        sa.UniqueConstraint("broker", name=op.f("uq_mstbroker_broker")),
    )

    op.create_index("idx_mstbroker_broker", "mstbroker", ["broker"])

    op.create_table(
        "mststate",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("state", sa.String(25), nullable=False),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_mststate")),
        sa.UniqueConstraint("state", name=op.f("uq_mststate_state")),
    )

    op.create_index("idx_mststate_state", "mststate", ["state"])

    op.create_table(
        "mstcity",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("state_id", sa.Integer(), nullable=False),
        sa.Column("city", sa.String(25), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["state_id"],
            ["mststate.id"],
            name=op.f("fk_mstcity_state_id_mststate"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_mstcity")),
    )

    op.create_index("idx_mstcity_city", "mstcity", ["city"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("mstmodel")
    op.drop_table("mstmake")
    op.drop_table("mstbranch")
    op.drop_table("mstsource")
    op.drop_table("mstyear")
    op.drop_table("mstbroker")
    op.drop_table("mstcity")
    op.drop_table("mststate")


# insert into mstmake
# (make,is_premium,created_by)
# values
# ('Audi',true,'Harshang'),
# ('Maruti',false,'Harshang');

# insert into mstmodel
# (make_id,model,created_by)
# values
# (1,'A3','Harshang'),
# (1,'A4','Harshang'),
# (2,'Waganor','Harshang'),
# (2,'Alto','Harshang'),
# (2,'XL6','Harshang');

# insert into mstbranch
# (branch,created_by)
# values
# ('YMCA','Harshang'),
# ('Soliter Connect','Harshang');

# insert into mstsource
# (source,created_by)
# values
# ('Website','Harshang'),
# ('Broker','Harshang');


# insert into mstyear
# (year)
# values
# (2026),
# (2025);

# insert into mstbroker
# (broker,created_by)
# values
# ('ABC','Harshang'),
# ('Test Test','Harshang');

# insert into mststate
# (state,created_by)
# values
# ('Gujarat','Harshang'),
# ('Maharastra','Harshang');

# insert into mstcity
# (state_id,city,created_by)
# values
# (1,'Ahmedabad','Harshang'),
# (1,'Surat','Harshang'),
# (2,'Bombay','Harshang'),
# (2,'Pune','Harshang');
