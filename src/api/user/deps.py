from fastapi import Depends
from sqlalchemy.orm import Session

from api.deps import get_db_session
from repository.user.user_repository import UserRepository
from repository.user.user_repository_interface import UserRepositoryInterface
from services.user.user_service import UserService
from services.user.user_service_interface import UserServiceInterface


def get_user_repository(
    sesion: Session = Depends(get_db_session),
) -> UserRepositoryInterface:
    return UserRepository(sesion)


async def user_service(
    user_repository: UserRepositoryInterface = Depends(get_user_repository),
) -> UserServiceInterface:
    return UserService(user_repository)
