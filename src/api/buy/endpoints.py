from uuid import UUID, uuid4

from fastapi import (APIRouter, BackgroundTasks, Body, Depends, File, Form,
                     HTTPException, Query, Request, UploadFile, status)

from api.buy import deps, example
from api.deps import get_authenticated_user, get_trace_id
from app import constant
from app.core.config import settings
from app.core.logging import logger
from auth.dto import AuthenticatedUser
from auth.exceptions import CreationError, NotFound
from common.csv_utils import stream_csv
from common.cursor_pagination import build_next_page_url, normalize_limit
from common.schema_types import (BuyStatus, FileStatus, SortOrder,
                                 validate_file_extension, validate_file_size)
from schema.buy.buy import (AllocateLeadsRequest, BuyLeadFollowupDetail,
                            BuyLeadFollowupList, BuyLeadItem, BuyLeadList,
                            BuyLeadSortBy, CreateBuyLead,
                            CreateBuyLeadFollowup, Response, UpdateBuyLead)
from services.buy.buy_service_interface import BuyServiceInterface

router = APIRouter(prefix="/buy", tags=["buy"])


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


@router.put(
    "/{lead_id}",
    response_model=Response,
    status_code=status.HTTP_200_OK,
)
async def update_lead(
    request: Request,
    lead_id: int,
    lead: UpdateBuyLead = Body(..., example=example.UPDATE_LEAD),
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> Response:
    logger.info(f"request: {request}")

    try:
        await buy_service.update_lead(lead_id, lead.to_model(), current_user.user_name)

    except NotFound as ex:
        logger.error(f"Not Found error: {ex}")
        raise HTTPException(status.HTTP_404_NOT_FOUND, constant.NOTFOUND)
    except ValueError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.VALUEERROR)
    except Exception as ex:
        logger.error(f"[{trace_id}] update_lead failed: {str(ex)}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)

    return Response(id=lead_id, message=constant.UPDATED)


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
    leads = buy_service.get_lead_export(
        search, buy_status, sort_by.value, sort_order.value
    )
    return stream_csv(rows=leads, filename="buy_lead_export.csv")


@router.get(
    "/lead/{lead_id}",
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
            raise HTTPException(status.HTTP_404_NOT_FOUND, constant.NOTFOUND)
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
async def remove_buy_lead_by_id(
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
            raise HTTPException(status.HTTP_404_NOT_FOUND, constant.NOTFOUND)

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
            raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.MAXLIMITREACH)
        alocate_count = await buy_service.allocate_leads(
            allocate.to_model(), current_user.user_name
        )
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


@router.patch(
    "/re-allocation",
    response_model=Response,
    status_code=status.HTTP_200_OK,
)
async def reallocate_leads(
    request: Request,
    reallocate: AllocateLeadsRequest = Body(..., example=example.BUY_LEAD_ALLOCATION),
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> Response:
    logger.info(f"request: {request}, user: {current_user}, reallocate:{reallocate}")
    try:
        if len(reallocate.lead_ids) > constant.MAX_LIMIT:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.MAXLIMITREACH)
        realocate_count = await buy_service.reallocate_leads(
            reallocate.to_model(), current_user.user_name
        )
        if realocate_count > 0:
            return Response(id=realocate_count, message=constant.CREATED)
        else:
            return Response(id=realocate_count, message=constant.FAILED)
    except ValueError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.VALUEERROR)
    except Exception as ex:
        logger.error(f"Exception error: {ex}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)


@router.post(
    "/{lead_id}/followup",
    response_model=Response,
    status_code=status.HTTP_201_CREATED,
)
async def create_lead_followup(
    request: Request,
    lead_id: int,
    lead: CreateBuyLeadFollowup = Body(..., example=example.BUY_LEAD_FOLLOWUP),
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> Response:
    logger.info(f"request: {request}")
    try:
        followup_id = await buy_service.create_lead_followup(
            lead_id=lead_id, lead=lead.to_model(), created_by=current_user.user_name
        )
    except CreationError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.FAILED)
    except ValueError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.VALUEERROR)
    except Exception as ex:
        logger.error(f"[{trace_id}] create_lead_followup failed: {str(ex)}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)
    return Response(id=followup_id, message=constant.CREATED)


@router.get(
    "/followup",
    response_model=BuyLeadFollowupList,
    status_code=status.HTTP_200_OK,
)
async def get_buy_followup_lead(
    request: Request,
    cursor: int | None = None,
    limit: int | None = None,
    search: str | None = None,
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> BuyLeadFollowupList:

    logger.info(f"request: {request}, user: {current_user}")
    try:
        limit = normalize_limit(limit)
        leads = await buy_service.get_followup_lead(
            cursor, limit, current_user.user_name, current_user.role_id, search
        )
        total = await buy_service.get_total_followup_lead(
            current_user.user_name, current_user.role_id, search
        )

        next_url = None
        if len(leads) == limit:
            last_id = leads[-1].id
            next_url = build_next_page_url(request, last_id, limit)

        return BuyLeadFollowupList(total=total, limit=limit, next=next_url, items=leads)
    except ValueError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.VALUEERROR)
    except Exception as ex:
        logger.error(f"Exception error: {ex}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)


@router.get(
    "/followup/export",
    status_code=status.HTTP_200_OK,
)
async def export_followup_lead(
    request: Request,
    search: str | None = None,
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
):
    leads = buy_service.get_followup_lead_export(
        current_user.user_name, current_user.role_id, search
    )
    return stream_csv(rows=leads, filename="buy_followup_export.csv")


@router.get(
    "/followup/lead/{lead_id}",
    response_model=BuyLeadFollowupDetail,
    status_code=status.HTTP_200_OK,
)
async def get_buy_followup_lead_by_id(
    request: Request,
    lead_id: int,
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> BuyLeadFollowupDetail:
    logger.info(f"request: {request}, user: {current_user}, id:{lead_id}")
    try:
        lead = await buy_service.get_followup_lead_by_id(
            lead_id, current_user.user_name, current_user.role_id
        )
        if not lead:
            logger.info(f"Not Found: {lead_id}")
            raise HTTPException(status.HTTP_404_NOT_FOUND, constant.NOTFOUND)
        return lead
    except HTTPException:
        raise
    except ValueError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.VALUEERROR)
    except Exception as ex:
        logger.error(f"Exception error: {ex}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)


@router.post("/import", response_model=Response, status_code=201)
async def import_buy_lead(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    source: str = Form(...),
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> Response:
    logger.info(f"request: {request}, user: {current_user}, filename: {file.filename}")
    try:

        file_uuid = uuid4()
        filename = file.filename.strip()

        await validate_file_extension(file, settings.allowed_extensions)

        await validate_file_size(file)

        s3_filename = f"leads/{source}/{file_uuid}/{filename}"
        s3_key = await buy_service.buy_lead_file_upload(
            filename=s3_filename,
            file_obj=file.file,
            content_type=file.content_type,
        )

        buy_file_id = await buy_service.create_lead_file_id(
            file_uuid=file_uuid, s3_key=s3_key, status=FileStatus.Pending.value
        )

        background_tasks.add_task(buy_service.process_file, file_uuid)
    except HTTPException:
        raise
    except CreationError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.FAILED)
    except ValueError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.VALUEERROR)
    except Exception as ex:
        logger.error(f"[{trace_id}] create_lead failed: {str(ex)}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)
    return Response(id=buy_file_id, message=constant.REQUEST)
