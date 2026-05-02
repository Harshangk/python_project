"""create tblinsurance_company

Revision ID: 3d4dd810c76e
Revises: c0d626eb7bef
Create Date: 2026-05-02 18:25:06.597200

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3d4dd810c76e"
down_revision: Union[str, Sequence[str], None] = "c0d626eb7bef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tblinsurance_company",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, increment=1),
            nullable=False,
        ),
        sa.Column("insurance_company_name", sa.String(255), nullable=False),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tblinsurance_company")),
        sa.UniqueConstraint(
            "insurance_company_name",
            name=op.f("uq_tblinsurance_company_insurance_company_name"),
        ),
    )

    op.create_index(
        "idx_tblinsurance_company_insurance_company_name",
        "tblinsurance_company",
        ["insurance_company_name"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("tblinsurance_company")


# insert into tblinsurance_company
# (insurance_company_name,created_by)
# values
# ('National Insurance Co Ltd','Harshang'),
# ('The Oriental Insurance Co Ltd','Harshang');
