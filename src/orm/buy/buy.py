from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Identity, Index,
                        Integer, String, Table)

from common.db import mapper_registry
from model.buy import buy as BuyModel

tblbuylead = Table(
    "tblbuylead",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
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
    Column("client_offer", Integer, default=0, nullable=False),
    Column("our_offer", Integer, default=0, nullable=False),
    Column("status", String(25), nullable=False),
    Column("telecaller", String(50), nullable=True),
    Column("executive", String(50), nullable=True),
    Column("remarks", String(500), nullable=False),
    Column("allocated_at", DateTime, nullable=True),
    Column("allocated_by", String(length=50), nullable=True),
    Column("created_at", DateTime, default=datetime.now, nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_deleted", Boolean, default=False, nullable=False),
    Index("idx_tblbuylead_mobile", "mobile"),
    Index("idx_tblbuylead_status", "status"),
    Index("idx_tblbuylead_telecaller", "telecaller"),
    Index("idx_tblbuylead_executive", "executive"),
)


def start_mappers() -> None:
    mapper_registry.map_imperatively(BuyModel.BuyLead, tblbuylead)


def stop_mappers() -> None:
    mapper_registry.dispose()
