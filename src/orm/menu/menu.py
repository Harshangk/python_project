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
from model.menu import menu as MenuModel

mstmenu = Table(
    "mstmenu",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("menu_name", String(length=50), nullable=False),
    Column("menu_icon", String(length=50), nullable=True),
    Column("menu_path", String(length=255), nullable=True),
    Column("parent_id", Integer(), ForeignKey("mstmenu.id"), nullable=True),
    Column("order_no", Integer(), nullable=False),
    Column("badge_count", Integer(), server_default=text("0"), nullable=False),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("is_active", Boolean, server_default=text("true"), nullable=False),
    Column("is_deleted", Boolean, server_default=text("false"), nullable=False),
)

maprolemenu = Table(
    "maprolemenu",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("role_id", Integer(), ForeignKey("mstrole.id"), nullable=False),
    Column("menu_id", Integer(), ForeignKey("mstmenu.id"), nullable=False),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    Column("is_active", Boolean, server_default=text("true"), nullable=False),
    Column("is_deleted", Boolean, server_default=text("false"), nullable=False),
    UniqueConstraint("role_id", "menu_id", name="uq_maprolemenu_role_id_menu_id"),
    Index("idx_maprolemenu_role_id", "role_id"),
    Index("idx_maprolemenu_menu_id", "menu_id"),
)


def start_mappers() -> None:
    mapper_registry.map_imperatively(MenuModel.Menu, mstmenu)
    mapper_registry.map_imperatively(MenuModel.RoleMenu, maprolemenu)


def stop_mappers() -> None:
    mapper_registry.dispose()
