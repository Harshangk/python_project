from fastapi import Depends
from sqlalchemy.orm import Session

from api.deps import get_db_session
from repository.menu.menu_repository import MenuRepository
from repository.menu.menu_repository_interface import MenuRepositoryInterface
from services.menu.menu_service import MenuService
from services.menu.menu_service_interface import MenuServiceInterface


def get_menu_repository(
    sesion: Session = Depends(get_db_session),
) -> MenuRepositoryInterface:
    return MenuRepository(sesion)


async def menu_service(
    menu_repository: MenuRepositoryInterface = Depends(get_menu_repository),
) -> MenuServiceInterface:
    return MenuService(menu_repository)
