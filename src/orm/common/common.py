from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Identity, Index,
                        Integer, String, Table, UniqueConstraint)

from common.db import mapper_registry
from model.common import common as CommonModel


mstmake = Table(
    "mstmake",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("make", String(50), nullable=False),
    Column("is_premium", Boolean, default=False, nullable=False),
    Column("created_at", DateTime, default=datetime.now, nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_deleted", Boolean, default=False, nullable=False),
    UniqueConstraint("make", name="uq_mstmake_make"),
    Index("idx_mstmake_make", "make"),
)

mstmodel = Table(
    "mstmodel",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("make_id", Integer(), ForeignKey("mstmake.id"), nullable=False),
    Column("model", String(50), nullable=False),
    Column("created_at", DateTime, default=datetime.now, nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_deleted", Boolean, default=False, nullable=False),
    UniqueConstraint("make_id", "model", name="uq_mstmodel_make_id_model"),
    Index("idx_mstmodel_model", "model"),
)

mstbranch = Table(
    "mstbranch",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("branch", String(50), nullable=False),
    Column("created_at", DateTime, default=datetime.now, nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_deleted", Boolean, default=False, nullable=False),
    UniqueConstraint("branch"),
    Index("idx_mstbranch_branch", "branch"),
)

mstsource = Table(
    "mstsource",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("source", String(50), nullable=False),
    Column("created_at", DateTime, default=datetime.now, nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_deleted", Boolean, default=False, nullable=False),
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
    Column("created_at", DateTime, default=datetime.now, nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_deleted", Boolean, default=False, nullable=False),
    UniqueConstraint("broker"),
    Index("idx_mstbroker_broker", "broker"),
)

mststate = Table(
    "mststate",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("state", String(25), nullable=False),
    Column("created_at", DateTime, default=datetime.now, nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_deleted", Boolean, default=False, nullable=False),
    UniqueConstraint("state"),
    Index("idx_mststate_state", "state"),
)

mstcity = Table(
    "mstcity",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("state_id", Integer(), ForeignKey("mststate.id"), nullable=False),
    Column("city", String(25), nullable=False),
    Column("created_at", DateTime, default=datetime.now, nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_deleted", Boolean, default=False, nullable=False),
    Index("idx_mstcity_city", "city"),
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


def stop_mappers() -> None:
    mapper_registry.dispose()
