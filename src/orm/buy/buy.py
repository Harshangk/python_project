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
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID

from common.db import mapper_registry
from model.buy import buy as BuyModel

tblbuylead = Table(
    "tblbuylead",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("branch", String(50), nullable=False),
    Column("mobile", String(15), nullable=False),
    Column("alternate_mobile", String(15), nullable=True),
    Column("source", String(50), nullable=False),
    Column("mode", String(25), nullable=False),
    Column("broker_name", String(255), nullable=True),
    Column("customer_name", String(255), nullable=False),
    Column("make_id", Integer, ForeignKey("mstmake.id"), nullable=False),
    Column("model_id", Integer, ForeignKey("mstmodel.id"), nullable=False),
    Column("variant", String(255), nullable=True),
    Column("color", String(50), nullable=True),
    Column("fuel_type", String(50), nullable=False),
    Column("year", String(4), nullable=False),
    Column("kms", Integer, nullable=False),
    Column("owner", String(1), nullable=False),
    Column("client_offer", Integer, server_default=text("0"), nullable=False),
    Column("our_offer", Integer, server_default=text("0"), nullable=False),
    Column("status", String(25), nullable=False),
    Column("telecaller", String(50), nullable=True),
    Column("executive", String(50), nullable=True),
    Column("remarks", String(500), nullable=False),
    Column("allocated_at", DateTime, nullable=True),
    Column("allocated_by", String(length=50), nullable=True),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    Column("is_active", Boolean, server_default=text("true"), nullable=False),
    Column("is_deleted", Boolean, server_default=text("false"), nullable=False),
    Column("import_id", UUID(as_uuid=True), nullable=True),
    Index("idx_tblbuylead_branch", "branch"),
    Index("idx_tblbuylead_mobile", "mobile"),
    Index("idx_tblbuylead_status", "status"),
    Index("idx_tblbuylead_telecaller", "telecaller"),
    Index("idx_tblbuylead_executive", "executive"),
)

tblbuylead_address = Table(
    "tblbuylead_address",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("buylead_id", Integer, ForeignKey("tblbuylead.id"), nullable=False),
    Column("address", String(100), nullable=False),
    Column("state", String(25), nullable=False),
    Column("city", String(25), nullable=False),
    Column("area", String(25), nullable=False),
    Column("pincode", Integer(), nullable=True),
    UniqueConstraint("buylead_id", name="uq_tblbuylead_address_buylead_id"),
)

tblbuylead_followup = Table(
    "tblbuylead_followup",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("buylead_id", Integer, ForeignKey("tblbuylead.id"), nullable=False),
    Column("stage", String(25), nullable=False),
    Column("disposition", String(50), nullable=False),
    Column("calldate", DateTime, nullable=True),
    Column("preferred_time", String(20), nullable=True),
    Column("notes", String(500), nullable=False),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("created_by", String(length=50), nullable=False),
    UniqueConstraint("buylead_id", name="uq_tblbuylead_followup_buylead_id"),
)

tblbuylead_file = Table(
    "tblbuylead_file",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("s3_key", Text(), nullable=False),
    Column("file_status", String(10), nullable=False),
    Column("file_uuid", UUID(as_uuid=True), nullable=False),
    Column("processed_records", Integer, server_default=text("0"), nullable=False),
    Column("error_records", Integer, server_default=text("0"), nullable=False),
    Column("error_s3_key", Text(), nullable=True),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("created_by", String(length=50), nullable=False),
    UniqueConstraint("file_uuid", name="uq_tblbuylead_file_file_uuid"),
    Index("idx_tblbuylead_file_file_uuid", "file_uuid"),
)


def start_mappers() -> None:
    mapper_registry.map_imperatively(BuyModel.BuyLead, tblbuylead)
    mapper_registry.map_imperatively(BuyModel.BuyLeadAddress, tblbuylead_address)
    mapper_registry.map_imperatively(BuyModel._BuyLeadFollowup, tblbuylead_followup)
    mapper_registry.map_imperatively(BuyModel.BuyLeadFile, tblbuylead_file)


def stop_mappers() -> None:
    mapper_registry.dispose()
