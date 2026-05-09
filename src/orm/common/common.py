from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    Table,
    UniqueConstraint,
    text,
)

from common.db import mapper_registry
from model.common import common as CommonModel

mstmake = Table(
    "mstmake",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("make", String(50), nullable=False),
    Column("is_premium", Boolean, server_default=text("false"), nullable=False),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    Column("is_active", Boolean, server_default=text("true"), nullable=False),
    Column("is_deleted", Boolean, server_default=text("false"), nullable=False),
    UniqueConstraint("make", name="uq_mstmake_make"),
    Index("idx_mstmake_make", "make"),
)

mstmodel = Table(
    "mstmodel",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("make_id", Integer(), ForeignKey("mstmake.id"), nullable=False),
    Column("model", String(50), nullable=False),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    Column("is_active", Boolean, server_default=text("true"), nullable=False),
    Column("is_deleted", Boolean, server_default=text("false"), nullable=False),
    UniqueConstraint("make_id", "model", name="uq_mstmodel_make_id_model"),
    Index("idx_mstmodel_model", "model"),
)

mstbranch = Table(
    "mstbranch",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("branch", String(50), nullable=False),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    Column("is_active", Boolean, server_default=text("true"), nullable=False),
    Column("is_deleted", Boolean, server_default=text("false"), nullable=False),
    UniqueConstraint("branch"),
    Index("idx_mstbranch_branch", "branch"),
)

mstsource = Table(
    "mstsource",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("source", String(50), nullable=False),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    Column("is_active", Boolean, server_default=text("true"), nullable=False),
    Column("is_deleted", Boolean, server_default=text("false"), nullable=False),
    UniqueConstraint("source"),
    Index("idx_mstsource_source", "source"),
)

mstyear = Table(
    "mstyear",
    mapper_registry.metadata,
    Column("year", Integer, primary_key=True, autoincrement=False),
)

mstbroker = Table(
    "mstbroker",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("broker", String(255), nullable=False),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    Column("is_active", Boolean, server_default=text("true"), nullable=False),
    Column("is_deleted", Boolean, server_default=text("false"), nullable=False),
    UniqueConstraint("broker"),
    Index("idx_mstbroker_broker", "broker"),
)

mststate = Table(
    "mststate",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("state", String(25), nullable=False),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    Column("is_active", Boolean, server_default=text("true"), nullable=False),
    Column("is_deleted", Boolean, server_default=text("false"), nullable=False),
    UniqueConstraint("state"),
    Index("idx_mststate_state", "state"),
)

mstcity = Table(
    "mstcity",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("state_id", Integer(), ForeignKey("mststate.id"), nullable=False),
    Column("city", String(25), nullable=False),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    Column("is_active", Boolean, server_default=text("true"), nullable=False),
    Column("is_deleted", Boolean, server_default=text("false"), nullable=False),
    Index("idx_mstcity_city", "city"),
)

tblbank = Table(
    "tblbank",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("bank_name", String(255), nullable=False),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    Column("is_active", Boolean, server_default=text("true"), nullable=False),
    Column("is_deleted", Boolean, server_default=text("false"), nullable=False),
    UniqueConstraint("bank_name"),
    Index("idx_tblbank_bank_name", "bank_name"),
)

tblinsurance_company = Table(
    "tblinsurance_company",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("insurance_company_name", String(255), nullable=False),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    Column("is_active", Boolean, server_default=text("true"), nullable=False),
    Column("is_deleted", Boolean, server_default=text("false"), nullable=False),
    UniqueConstraint("insurance_company_name"),
    Index("idx_tblinsurance_company_insurance_company_name", "insurance_company_name"),
)


mstpart = Table(
    "mstpart",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("part_name", String(length=50), nullable=False),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    Column("is_active", Boolean, server_default=text("true"), nullable=False),
    Column("is_deleted", Boolean, server_default=text("false"), nullable=False),
    UniqueConstraint("part_name", name="uq_mstpart_part_name"),
)

mstsubpart = Table(
    "mstsubpart",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("part_id", Integer(), ForeignKey("mstpart.id"), nullable=False),
    Column("subpart_name", String(50), nullable=False),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    Column("is_active", Boolean, server_default=text("true"), nullable=False),
    Column("is_deleted", Boolean, server_default=text("false"), nullable=False),
    Index("idx_mstsubpart_part_id", "part_id"),
)

mstsubpartstatus = Table(
    "mstsubpartstatus",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("subpart_id", Integer(), ForeignKey("mstsubpart.id"), nullable=False),
    Column("subpart_status", String(50), nullable=False),
    Column("is_default", Boolean, server_default=text("false"), nullable=False),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    Column("is_active", Boolean, server_default=text("true"), nullable=False),
    Column("is_deleted", Boolean, server_default=text("false"), nullable=False),
    Index("idx_mstsubpartstatus_subpart_id", "subpart_id"),
)

mstsubpartsubstatus = Table(
    "mstsubpartsubstatus",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column(
        "subpartstatus_id", Integer(), ForeignKey("mstsubpartstatus.id"), nullable=False
    ),
    Column("subpart_sub_status", String(50), nullable=False),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    Column("is_active", Boolean, server_default=text("true"), nullable=False),
    Column("is_deleted", Boolean, server_default=text("false"), nullable=False),
    Index("idx_mstsubpartsubstatus_subpartstatus_id", "subpartstatus_id"),
)


def start_mappers() -> None:
    mapper_registry.map_imperatively(CommonModel.Make, mstmake)
    mapper_registry.map_imperatively(CommonModel.Model, mstmodel)
    mapper_registry.map_imperatively(CommonModel.Branch, mstbranch)
    mapper_registry.map_imperatively(CommonModel.Source, mstsource)
    mapper_registry.map_imperatively(CommonModel.Year, mstyear)
    mapper_registry.map_imperatively(CommonModel.Broker, mstbroker)
    mapper_registry.map_imperatively(CommonModel.State, mststate)
    mapper_registry.map_imperatively(CommonModel.City, mstcity)
    mapper_registry.map_imperatively(CommonModel.Bank, tblbank)
    mapper_registry.map_imperatively(CommonModel.InsuranceCompany, tblinsurance_company)
    mapper_registry.map_imperatively(CommonModel.Part, mstpart)
    mapper_registry.map_imperatively(CommonModel.SubPart, mstsubpart)
    mapper_registry.map_imperatively(CommonModel.SubPartStatus, mstsubpartstatus)
    mapper_registry.map_imperatively(CommonModel.SubPartSubStatus, mstsubpartsubstatus)


def stop_mappers() -> None:
    mapper_registry.dispose()
