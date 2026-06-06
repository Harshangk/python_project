from functools import cache

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings


@cache
def get_mongo_client() -> AsyncIOMotorClient:
    """Cached MongoDB client. Reused across all calls."""
    if not settings.mongo_uri:
        raise RuntimeError("MONGO_URI not configured (settings.mongo_uri)")
    return AsyncIOMotorClient(settings.mongo_uri)


@cache
def get_mongo_db():
    """Cached MongoDB database instance."""
    db_name = settings.mongo_database
    return get_mongo_client()[db_name]


def get_mongo_collection(name: str):
    """Get a MongoDB collection by name."""
    return get_mongo_db()[name]
