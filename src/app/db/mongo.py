from functools import cache

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings


@cache
def get_mongo_client() -> AsyncIOMotorClient:
    if not settings.mongo_uri:
        raise RuntimeError("MONGO_URI not configured (settings.mongo_uri)")
    return AsyncIOMotorClient(
        settings.mongo_uri,
        maxPoolSize=10,
        minPoolSize=1,
        connectTimeoutMS=5000,
        serverSelectionTimeoutMS=5000,
    )


@cache
def get_mongo_db():
    return get_mongo_client()[settings.mongo_database]


def get_mongo_collection(name: str):
    return get_mongo_db()[name]


async def setup_mongo_indexes():
    try:
        coll = get_mongo_collection("buylead_followup_history")
        await coll.create_index("buylead_id")
    except Exception:
        raise RuntimeError(
            "Failed to create MongoDB indexes, check connection and configuration"
        )


def close_mongo_client():
    client = get_mongo_client()
    client.close()
