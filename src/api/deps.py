from functools import cache
from typing import AsyncGenerator, Callable
from uuid import UUID, uuid4

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import SessionLocal
from app.s3 import get_s3_client
from auth.dto import AuthenticatedActor, AuthenticatedUser
from auth.factory import make_auth_service_factory
from auth.services import AbstractAuthService, FakeAuthService
from common.file_storage import (AbstractFileStorage, LocalFileStorage,
                                 S3FileStorage)
from common.utils import trace_id_var


def get_trace_id(x_trace_id: UUID = Header(None)):
    if x_trace_id:
        trace_id_var.set(x_trace_id)
        return x_trace_id

    new_trace = uuid4()
    trace_id_var.set(new_trace)
    return new_trace


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


@cache
def _fake_auth_service() -> AbstractAuthService:
    return FakeAuthService()


_get_auth_service: Callable[[], AbstractAuthService]
if not settings.application_env or settings.application_env == "Local":
    _get_auth_service = _fake_auth_service
else:
    _get_auth_service = make_auth_service_factory()


def get_authenticated_user(
    auth_service: AbstractAuthService = Depends(_get_auth_service),
) -> AuthenticatedUser:
    return auth_service.authenticated_user


def get_authenticated_actor(
    auth_service: AbstractAuthService = Depends(_get_auth_service),
) -> AuthenticatedActor:
    return auth_service.authenticated_actor


def get_file_storage_object(bucket: str | None) -> Callable[[], AbstractFileStorage]:
    def generate_storage_object() -> AbstractFileStorage:
        # storage: AbstractFileStorage
        if settings.application_env == "local":
            return LocalFileStorage("static")
        elif settings.application_env == "prod" or settings.s3_acess_key_id:
            if not bucket:
                raise RuntimeError("No S3 Bucket provided")
            return S3FileStorage(client=get_s3_client(), bucket_name=bucket)
        else:
            return LocalFileStorage("static")

    return generate_storage_object
