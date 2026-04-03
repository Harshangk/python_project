from sqlalchemy import MetaData as BaseMetaData
from sqlalchemy import Table
from sqlalchemy.orm import DeclarativeMeta, registry


class MetaData(BaseMetaData):
    def __repr__(self):
        # enables access to the metadata in alembic.
        # see `alembic.env.render_item`
        return "Base.metadata"


meta = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    },
)
mapper_registry: registry = registry(metadata=meta)


class Base(metaclass=DeclarativeMeta):
    __abstract__ = True
    registry = mapper_registry
    metadata = mapper_registry.metadata
    __init__ = mapper_registry.constructor

    __name__: str
    __table__: Table
