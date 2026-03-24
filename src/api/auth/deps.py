from fastapi import Depends
from sqlalchemy.orm import Session

from api.deps import get_db_session
from repository.auth.auth_repository import AuthRepository
from repository.auth.auth_repository_interface import AuthRepositoryInterface
from services.auth.auth_service import AuthService
from services.auth.auth_service_interface import AuthServiceInterface


def get_auth_repository(
    sesion: Session = Depends(get_db_session),
) -> AuthRepositoryInterface:
    return AuthRepository(sesion)


async def auth_service(
    auth_repository: AuthRepositoryInterface = Depends(get_auth_repository),
) -> AuthServiceInterface:
    return AuthService(auth_repository)
