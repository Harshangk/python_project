from fastapi import Depends
from sqlalchemy.orm import Session

from api.deps import get_db_session, get_file_storage_object
from app.core.config import settings
from common.file_storage import AbstractFileStorage
from repository.common.common_repository import CommonRepository
from repository.common.common_repository_interface import CommonRepositoryInterface
from services.common.common_service import CommonService
from services.common.common_service_interface import CommonServiceInterface


def get_common_repository(
    sesion: Session = Depends(get_db_session),
) -> CommonRepositoryInterface:
    return CommonRepository(sesion)


buy_lead_file_storage = get_file_storage_object(settings.s3_bucket_name)
buy_lead_file_storage_error = get_file_storage_object(settings.error_s3_bucket_name)


async def common_service(
    common_repository: CommonRepositoryInterface = Depends(get_common_repository),
    file_storage: AbstractFileStorage = Depends(buy_lead_file_storage),
    error_file_storage: AbstractFileStorage = Depends(buy_lead_file_storage_error),
) -> CommonServiceInterface:
    return CommonService(common_repository, file_storage, error_file_storage)
