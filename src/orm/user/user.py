from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Identity, Index,
                        Integer, String, Table, UniqueConstraint)

from common.db import mapper_registry
from model.user import user as UserModel

mstrole = Table(
    "mstrole",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("role", String(length=15), nullable=False),
    Column("created_at", DateTime, default=datetime.now, nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_deleted", Boolean, default=False, nullable=False),
    UniqueConstraint("role", name="uq_mstrole_role"),
)

mstlogin = Table(
    "mstlogin",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("role_id", Integer(), ForeignKey("mstrole.id"), nullable=False),
    Column("user_name", String(length=50), nullable=False),
    Column("password", String(), nullable=False),
    Column("last_login", DateTime, nullable=True),
    Column("login_at", DateTime, nullable=True),
    Column("created_at", DateTime, default=datetime.now, nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    Column("expiry_at", DateTime, nullable=True),
    Column("is_lock", Boolean, default=False, nullable=False),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_deleted", Boolean, default=False, nullable=False),
    UniqueConstraint("user_name"),
    Index("idx_mstlogin_role_id", "role_id"),
    Index("idx_mstlogin_user_name", "user_name"),
)


def start_mappers() -> None:
    mapper_registry.map_imperatively(UserModel.User, mstlogin)


def stop_mappers() -> None:
    mapper_registry.dispose()
