from fastapi import Depends
from sqlalchemy.orm import Session

from api.deps import get_db_session, get_file_storage_object
from app.core.config import settings
from common.file_storage import AbstractFileStorage
from repository.buy.buy_repository import BuyRepository
from repository.buy.buy_repository_interface import BuyRepositoryInterface
from services.buy.buy_service import BuyService
from services.buy.buy_service_interface import BuyServiceInterface


def get_buy_repository(
    sesion: Session = Depends(get_db_session),
) -> BuyRepositoryInterface:
    return BuyRepository(sesion)


buy_lead_file_storage = get_file_storage_object(settings.s3_bucket_name)


async def buy_service(
    buy_repository: BuyRepositoryInterface = Depends(get_buy_repository),
    file_storage: AbstractFileStorage = Depends(buy_lead_file_storage),
) -> BuyServiceInterface:
    return BuyService(buy_repository, file_storage)
