from uuid import UUID

from fastapi import APIRouter, Depends, Request, status

from api.deps import get_authenticated_user, get_trace_id
from api.menu import deps
from app.core.logging import logger
from auth.dto import AuthenticatedUser
from schema.menu.menu import MenuResponse
from services.menu.menu_service_interface import MenuServiceInterface

router = APIRouter(prefix="/menu", tags=["menu"])


@router.get(
    "",
    response_model=list[MenuResponse],
    status_code=status.HTTP_200_OK,
)
async def get_menu(
    request: Request,
    menu_service: MenuServiceInterface = Depends(deps.menu_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> list[MenuResponse]:
    logger.info(request)
    menu = await menu_service.get_menu(current_user.role_id)
    return menu
