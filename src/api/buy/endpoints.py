from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from api.buy import deps
from api.deps import get_authenticated_user, get_trace_id
from api.schema_types import SortOrder
from app import constant
from app.core.logging import logger
from auth.dto import AuthenticatedUser
from auth.exceptions import CreationError
from common.csv_utils import stream_csv
from common.cursor_pagination import build_next_page_url, normalize_limit
from schema.buy.buy import BuyLeadList, BuyLeadSortBy, CreateBuyLead, Response
from services.buy.buy_service_interface import BuyServiceInterface

router = APIRouter(prefix="/buy", tags=["buy"])


@router.post(
    "",
    response_model=Response,
    status_code=status.HTTP_201_CREATED,
)
async def create_lead(
    request: Request,
    lead: CreateBuyLead,
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> Response:
    logger.info(f"request: {request}")
    try:
        buy_id = await buy_service.create_lead(lead.to_model(), current_user.user_name)
    except CreationError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.FAILED)
    except ValueError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.VALUEERROR)
    except Exception as ex:
        logger.error(f"[{trace_id}] create_lead failed: {str(ex)}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)
    return Response(id=buy_id, message=constant.CREATED)


@router.get(
    "",
    response_model=BuyLeadList,
    status_code=status.HTTP_200_OK,
)
async def get_buy_lead(
    request: Request,
    cursor: int | None = None,
    limit: int | None = None,
    search: str | None = None,
    sort_by: BuyLeadSortBy = Query(BuyLeadSortBy.id, description="Field to sort by"),
    sort_order: SortOrder = Query(SortOrder.desc, description="Sort direction"),
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> BuyLeadList:
    logger.info(f"request: {request}, user: {current_user}")
    try:
        limit = normalize_limit(limit)
        leads = await buy_service.get_lead(
            cursor, limit, search, sort_by.value, sort_order.value
        )
        total = await buy_service.get_total_lead(search)

        next_url = None
        if len(leads) == limit:
            last_id = leads[-1].id
            next_url = build_next_page_url(request, last_id, limit)

        return BuyLeadList(total=total, limit=limit, next=next_url, items=leads)
    except ValueError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.VALUEERROR)
    except Exception as ex:
        logger.error(f"Exception error: {ex}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)


@router.get(
    "/export",
    status_code=status.HTTP_200_OK,
)
async def export_lead(
    request: Request,
    search: str | None = None,
    sort_by: BuyLeadSortBy = Query(BuyLeadSortBy.id, description="Field to sort by"),
    sort_order: SortOrder = Query(SortOrder.desc, description="Sort direction"),
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
):
    leads = buy_service.get_lead_export(search, sort_by.value, sort_order.value)
    return stream_csv(rows=leads, filename="users_export.csv")
