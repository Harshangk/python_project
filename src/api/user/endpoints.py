from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from api.deps import get_authenticated_user, get_trace_id
from api.schema_types import SortOrder
from api.user import deps
from app import constant
from app.core.logging import logger
from auth.dto import AuthenticatedUser
from auth.exceptions import CreationError
from common.csv_utils import stream_csv
from common.cursor_pagination import build_next_page_url, normalize_limit
from schema.user.user import (CreateUser, Response, UserItem, UserList,
                              UserSortBy)
from services.user.user_service_interface import UserServiceInterface

router = APIRouter(prefix="/user", tags=["user"])


@router.get(
    "/me",
    response_model=AuthenticatedUser,
    status_code=status.HTTP_200_OK,
)
async def get_current_user(
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
) -> AuthenticatedUser:
    return current_user


@router.post(
    "",
    response_model=Response,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    request: Request,
    user: CreateUser,
    user_service: UserServiceInterface = Depends(deps.user_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> Response:
    try:
        user_id = await user_service.create_user(
            user.to_model(), current_user.user_name
        )
    except CreationError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.FAILED)
    return Response(id=user_id, message=constant.CREATED)


@router.get(
    "",
    response_model=UserList,
    status_code=status.HTTP_200_OK,
)
async def get_user(
    request: Request,
    cursor: int | None = None,
    limit: int | None = None,
    role_id: int | None = None,
    search: str | None = None,
    sort_by: UserSortBy = Query(UserSortBy.id, description="Field to sort by"),
    sort_order: SortOrder = Query(SortOrder.desc, description="Sort direction"),
    user_service: UserServiceInterface = Depends(deps.user_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
) -> UserList:
    logger.info(request)
    limit = normalize_limit(limit)
    users = await user_service.get_user(
        cursor, limit, role_id, search, sort_by.value, sort_order.value
    )
    total = await user_service.get_total_user(role_id, search)

    next_url = None
    if len(users) == limit:
        last_id = users[-1].id
        next_url = build_next_page_url(request, last_id, limit)

    return UserList(total=total, limit=limit, next=next_url, items=users)


@router.get(
    "/export",
    status_code=status.HTTP_200_OK,
)
async def export_user(
    request: Request,
    role_id: int | None = None,
    search: str | None = None,
    sort_by: UserSortBy = Query(UserSortBy.id, description="Field to sort by"),
    sort_order: SortOrder = Query(SortOrder.desc, description="Sort direction"),
    user_service: UserServiceInterface = Depends(deps.user_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
):
    users = user_service.get_user_export(role_id, search, sort_by.value, sort_order.value)
    return stream_csv(rows=users, filename="users_export.csv")


@router.get(
    "/{user_id}",
    response_model=UserItem,
    status_code=status.HTTP_200_OK,
)
async def get_user_by_id(
    user_id: int,
    request: Request,
    user_service: UserServiceInterface = Depends(deps.user_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
) -> UserItem:
    logger.info(f"Fetching user with id: {user_id}")

    user = await user_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=constant.NOTFOUND,
        )

    return user


@router.delete(
    "/{user_id}",
    response_model=Response,
    status_code=status.HTTP_200_OK,
)
async def delete_user(
    user_id: int,
    request: Request,
    user_service: UserServiceInterface = Depends(deps.user_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
) -> Response:
    logger.info(f"Deleting user with id: {user_id}")

    user = await user_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=constant.NOTFOUND,
        )

    await user_service.lock_user(user_id)

    return Response(id=user_id, message=constant.REMOVED)
