from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Body, Depends, File, Form, HTTPException, Query, Request, UploadFile, status

from api.buy import deps
from api.buy import example
from api.deps import get_authenticated_user, get_trace_id
from api.schema_types import SortOrder, BuyStatus
from app import constant
from app.core.logging import logger
from auth.dto import AuthenticatedUser
from auth.exceptions import CreationError
from common.csv_utils import stream_csv
from common.cursor_pagination import build_next_page_url, normalize_limit
from schema.buy.buy import (
    AllocateLeadsRequest,
    BuyLeadItem,
    BuyLeadList,
    BuyLeadSortBy,
    CreateBuyLead,
    GeneralResponse,
    Response,
)
from services.buy.buy_service_interface import BuyServiceInterface

router = APIRouter(prefix="/buy", tags=["buy"])

CSV_CONTENT_TYPES = {"text/csv", "application/csv", "application/vnd.ms-excel"}


@router.post(
    "",
    response_model=Response,
    status_code=status.HTTP_201_CREATED,
)
async def create_lead(
    request: Request,
    lead: CreateBuyLead = Body(..., example=example.BUY_LEAD),
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


@router.post(
    "/import",
    response_model=GeneralResponse,
    status_code=status.HTTP_201_CREATED,
)
async def import_lead(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    source: str = Form(...),
    broker_name: str | None = Form(None),
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> GeneralResponse:
    logger.info(f"request: {request}, user: {current_user}, filename: {file.filename}")
    try:
        filename = (file.filename or "").strip()
        if not filename:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "file name is required.",
            )

        if not filename.lower().endswith(".csv") or file.content_type not in CSV_CONTENT_TYPES:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "only CSV files are allowed.",
            )
        content = await file.read()
        await file.seek(0)
        background_tasks.add_task(
            buy_service.import_lead_content,
            content=content,
            filename=filename,
            source=source,
            broker_name=broker_name,
            created_by=current_user.user_name,
        )
        return GeneralResponse(detail=constant.RECIEVED_REQUEST)
    except HTTPException:
        raise
    except ValueError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(ex))
    except Exception as ex:
        logger.error(f"import_lead failed: {str(ex)}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)


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
    buy_status: BuyStatus | None = None,
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
            cursor, limit, search, buy_status, sort_by.value, sort_order.value
        )
        total = await buy_service.get_total_lead(search, buy_status)

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
    buy_status: BuyStatus | None = None,
    sort_by: BuyLeadSortBy = Query(BuyLeadSortBy.id, description="Field to sort by"),
    sort_order: SortOrder = Query(SortOrder.desc, description="Sort direction"),
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
):
    leads = await buy_service.get_lead_export(search, buy_status, sort_by.value, sort_order.value)
    return stream_csv(rows=leads, filename="users_export.csv")


@router.get(
    "/{lead_id}",
    response_model=BuyLeadItem,
    status_code=status.HTTP_200_OK,
)
async def get_buy_lead_by_id(
    request: Request,
    lead_id: int,
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> BuyLeadItem:
    logger.info(f"request: {request}, user: {current_user}, id:{lead_id}")
    try:
        lead = await buy_service.get_lead_by_id(lead_id)
        if not lead:
            logger.info(f"Not Found: {lead_id}")
            raise HTTPException(status.HTTP_404_NOT_FOUND,constant.NOTFOUND)
        return lead
    except HTTPException:
        raise
    except ValueError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.VALUEERROR)
    except Exception as ex:
        logger.error(f"Exception error: {ex}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)
    

@router.delete(
    "/{lead_id}",
    response_model=Response,
    status_code=status.HTTP_200_OK,
)
async def remove_buy_lead(
    request: Request,
    lead_id: int,
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> Response:
    logger.info(f"request: {request}, user: {current_user}, id:{id}")
    try:
        lead = await buy_service.get_lead_by_id(lead_id, current_user.user_name)
        if not lead:
            logger.info(f"Not Found: {id}")
            raise HTTPException(status.HTTP_404_NOT_FOUND,constant.NOTFOUND)
        
        await buy_service.remove_lead(lead_id)
        return Response(id=lead_id, message=constant.REMOVED)
    except HTTPException:
        raise
    except ValueError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.VALUEERROR)
    except Exception as ex:
        logger.error(f"Exception error: {ex}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)


@router.patch(
    "/allocation",
    response_model=Response,
    status_code=status.HTTP_200_OK,
)
async def allocate_leads(
    request: Request,
    allocate: AllocateLeadsRequest = Body(..., example=example.BUY_LEAD_ALLOCATION),
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> Response:
    logger.info(f"request: {request}, user: {current_user}, allocate:{allocate}")
    try:
        if len(allocate.lead_ids) > constant.MAX_LIMIT:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                constant.MAXLIMITREACH
            )
        alocate_count = await buy_service.allocate_leads(allocate.to_model(), current_user.user_name)
        if alocate_count > 0:
            return Response(id=alocate_count, message=constant.CREATED)
        else:
            return Response(id=alocate_count, message=constant.FAILED)
    except ValueError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.VALUEERROR)
    except Exception as ex:
        logger.error(f"Exception error: {ex}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)
