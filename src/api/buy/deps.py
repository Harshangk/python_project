from fastapi import Depends
from sqlalchemy.orm import Session

from api.deps import get_db_session
from repository.buy.buy_repository import BuyRepository
from repository.buy.buy_repository_interface import BuyRepositoryInterface
from services.buy.buy_service import BuyService
from services.buy.buy_service_interface import BuyServiceInterface


def get_buy_repository(
    sesion: Session = Depends(get_db_session),
) -> BuyRepositoryInterface:
    return BuyRepository(sesion)


async def buy_service(
    buy_repository: BuyRepositoryInterface = Depends(get_buy_repository),
) -> BuyServiceInterface:
    return BuyService(buy_repository)
