from functools import cache

from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from orm.user import user as UserORM


def get_url() -> URL:
    if not settings.database_url:
        raise RuntimeError(
            "No database configuration provided, set DATABASE_URI variable"
        )
    return make_url(settings.database_url)


@cache
def get_engine():
    UserORM.start_mappers()

    return create_async_engine(
        get_url(),
        pool_pre_ping=True,
        pool_size=20,
        max_overflow=10,
    )


SessionLocal = async_sessionmaker(
    bind=get_engine(),
    expire_on_commit=False,
)
