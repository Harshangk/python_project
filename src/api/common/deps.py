from fastapi import Depends
from sqlalchemy.orm import Session

from api.deps import get_db_session
from repository.common.common_repository import CommonRepository
from repository.common.common_repository_interface import \
    CommonRepositoryInterface
from services.common.common_service import CommonService
from services.common.common_service_interface import CommonServiceInterface


def get_common_repository(
    sesion: Session = Depends(get_db_session),
) -> CommonRepositoryInterface:
    return CommonRepository(sesion)


async def common_service(
    common_repository: CommonRepositoryInterface = Depends(get_common_repository),
) -> CommonServiceInterface:
    return CommonService(common_repository)
