import io
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    File,
    Form,
    HTTPException,
    Path,
    Query,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse

from api.buy import deps, example
from api.buy.validation import validate_evaluation_parameters
from api.common.deps import common_service
from api.deps import get_authenticated_user, get_trace_id
from app import constant
from app.core.config import settings
from app.core.logging import logger
from app.core.permission import require_roles
from auth.dto import AuthenticatedUser
from auth.exceptions import AlreadyExistsError, CreationError, NotFound
from common.csv_utils import stream_csv
from common.cursor_pagination import build_next_page_url, normalize_limit
from common.schema_types import (
    BuyStage,
    BuyStatus,
    FileStatus,
    SortOrder,
    validate_csv_headers,
    validate_file_extension,
    validate_file_size,
    validate_photos,
    validate_stockin_documents,
)
from schema.buy.buy import (
    AllocateLeadsRequest,
    BuyLeadFollowupDetail,
    BuyLeadFollowupList,
    BuyLeadImportItem,
    BuyLeadImportList,
    BuyLeadItem,
    BuyLeadList,
    BuyLeadSortBy,
    BuyTargetItem,
    BuyTargetList,
    CreateBuyLead,
    CreateBuyLeadFollowup,
    CreateBuyLeadPayment,
    CreateBuyTarget,
    ImportBuyLeadRequest,
    ProvideBuyLeadPreprice,
    Response,
    UpdateBuyLead,
    UpdateBuyTarget,
)
from services.buy.buy_service_interface import BuyServiceInterface
from services.common.common_service_interface import CommonServiceInterface

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
    except AlreadyExistsError as ex:
        logger.error(
            f"Lead already exists | " f"Lead ID: {ex.lead_id} | " f"Status: {ex.status}"
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": constant.EXISTS,
                "lead_id": ex.lead_id,
                "status": ex.status,
                "telecaller": ex.telecaller,
                "executive": ex.executive,
            },
        )
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
    lead_id: int = Path(..., gt=0),
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
            cursor,
            limit,
            current_user.user_name,
            current_user.role_id,
            search,
            buy_status,
            sort_by.value,
            sort_order.value,
        )
        total = await buy_service.get_total_lead(
            current_user.user_name, current_user.role_id, search, buy_status
        )

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
    logger.info(f"request: {request}, user: {current_user}")
    try:
        leads = buy_service.get_lead_export(
            current_user.user_name,
            current_user.role_id,
            search,
            buy_status,
            sort_by.value,
            sort_order.value,
        )
        return stream_csv(rows=leads, filename="buy_lead_export.csv")
    except Exception as ex:
        logger.error(f"[{trace_id}] export_buy_leads failed: {str(ex)}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)


@router.get(
    "/lead/{lead_id}",
    response_model=BuyLeadItem,
    status_code=status.HTTP_200_OK,
)
async def get_buy_lead_by_id(
    request: Request,
    lead_id: int = Path(..., gt=0),
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> BuyLeadItem:
    logger.info(f"request: {request}, user: {current_user}, id:{lead_id}")
    try:
        lead = await buy_service.get_lead_by_id(
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


@router.delete(
    "/{lead_id}",
    response_model=Response,
    status_code=status.HTTP_200_OK,
)
async def remove_buy_lead_by_id(
    request: Request,
    lead_id: int = Path(..., gt=0),
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> Response:
    logger.info(f"request: {request}, user: {current_user}, id:{id}")
    try:
        lead = await buy_service.get_lead_by_id(
            lead_id, current_user.user_name, current_user.role_id
        )
        if not lead:
            logger.info(f"Not Found: {id}")
            raise HTTPException(status.HTTP_404_NOT_FOUND, constant.NOTFOUND)

        await buy_service.remove_lead(
            lead_id, current_user.user_name, current_user.role_id
        )
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
            allocate.to_model(), current_user.user_name, current_user.role_id
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
            reallocate.to_model(), current_user.user_name, current_user.role_id
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


@router.patch(
    "/reopen",
    response_model=Response,
    status_code=status.HTTP_200_OK,
)
async def reopen_leads(
    request: Request,
    reopen: AllocateLeadsRequest = Body(..., example=example.BUY_LEAD_ALLOCATION),
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> Response:
    logger.info(f"request: {request}, user: {current_user}, allocate:{reopen}")
    try:
        if len(reopen.lead_ids) > constant.MAX_LIMIT:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.MAXLIMITREACH)
        reopen_count = await buy_service.reopen_leads(
            reopen.to_model(), current_user.user_name, current_user.role_id
        )
        if reopen_count > 0:
            return Response(id=reopen_count, message=constant.CREATED)
        else:
            return Response(id=reopen_count, message=constant.FAILED)
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
    lead_id: int = Path(..., gt=0),
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
    buy_stage: BuyStage | None = None,
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> BuyLeadFollowupList:

    logger.info(f"request: {request}, user: {current_user}")
    try:
        limit = normalize_limit(limit)
        leads = await buy_service.get_followup_lead(
            cursor,
            limit,
            current_user.user_name,
            current_user.role_id,
            search,
            buy_stage,
        )
        total = await buy_service.get_total_followup_lead(
            current_user.user_name, current_user.role_id, search, buy_stage
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
    "/followup/status/count",
    response_model=dict[str, int],
    status_code=status.HTTP_200_OK,
)
async def get_buy_followup_lead_status_count(
    request: Request,
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> dict[str, int]:

    logger.info(f"request: {request}, user: {current_user}")
    try:
        return await buy_service.get_followup_lead_status_count(
            current_user.user_name,
            current_user.role_id,
        )

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
    buy_stage: BuyStage | None = None,
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
):
    logger.info(f"request: {request}, user: {current_user}")
    try:
        leads = buy_service.get_followup_lead_export(
            current_user.user_name, current_user.role_id, search, buy_stage
        )
        return stream_csv(rows=leads, filename="buy_followup_export.csv")
    except Exception as ex:
        logger.error(f"[{trace_id}] export_buy_followup_leads failed: {str(ex)}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)


@router.get(
    "/followup/lead/{lead_id}",
    response_model=BuyLeadFollowupDetail,
    status_code=status.HTTP_200_OK,
)
async def get_buy_followup_lead_by_id(
    request: Request,
    lead_id: int = Path(..., gt=0),
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
    broker_name: str | None = Form(None),
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    commmon_service: CommonServiceInterface = Depends(common_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> Response:
    logger.info(f"request: {request}, user: {current_user}, filename: {file.filename}")
    try:
        data = ImportBuyLeadRequest(source=source, broker_name=broker_name)

        if not await commmon_service.validate_source(data.source):
            raise HTTPException(status_code=400, detail="Invalid source")

        if data.source.lower() == "broker":
            if not await commmon_service.validate_broker(data.broker_name):
                raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.BROKERINVALID)

        file_uuid = uuid4()
        filename = file.filename.strip()
        file_bytes = await file.read()

        await validate_file_extension(filename, settings.allowed_extensions)

        await validate_file_size(file_bytes)

        await validate_csv_headers(file_bytes, constant.BUYREQUIREDCOLUMS)

        s3_filename = f"{file_uuid}_{filename}"
        s3_key = await buy_service.buy_lead_file_upload(
            filename=s3_filename,
            file_bytes=file_bytes,
            content_type=file.content_type,
        )

        buy_file_id = await buy_service.create_lead_file_id(
            file_uuid=file_uuid,
            s3_key=s3_key,
            status=FileStatus.Pending.value,
            created_by=current_user.user_name,
        )
        background_tasks.add_task(
            buy_service.process_file,
            file_uuid,
            s3_key,
            current_user.user_name,
            data.source,
            data.broker_name,
        )
    except HTTPException as ex:
        logger.error(
            f"General HTTP exception [{trace_id}] \
                     import_buy_lead failed: {str(ex)}"
        )
        raise ex
    except CreationError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.FAILED)
    except ValueError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.VALUEERROR)
    except Exception as ex:
        logger.error(f"[{trace_id}] import_buy_lead failed: {str(ex)}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)
    return Response(id=buy_file_id, message=constant.REQUEST)


@router.get(
    "/import",
    response_model=BuyLeadImportList,
    status_code=status.HTTP_200_OK,
)
async def get_buy_import_lead(
    request: Request,
    cursor: int | None = None,
    limit: int | None = None,
    search: str | None = None,
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> BuyLeadImportList:

    logger.info(f"request: {request}, user: {current_user}")
    try:
        limit = normalize_limit(limit)
        leads = await buy_service.get_import_lead(
            cursor, limit, current_user.user_name, current_user.role_id, search
        )
        total = await buy_service.get_total_import_lead(
            current_user.user_name, current_user.role_id, search
        )

        next_url = None
        if len(leads) == limit:
            last_id = leads[-1].id
            next_url = build_next_page_url(request, last_id, limit)

        return BuyLeadImportList(total=total, limit=limit, next=next_url, items=leads)
    except ValueError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.VALUEERROR)
    except Exception as ex:
        logger.error(f"Exception error: {ex}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)


@router.get(
    "/import/export",
    status_code=status.HTTP_200_OK,
)
async def export_import_lead(
    request: Request,
    search: str | None = None,
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
):
    logger.info(f"request: {request}, user: {current_user}")
    try:
        leads = buy_service.get_import_lead_export(
            current_user.user_name, current_user.role_id, search
        )
        return stream_csv(rows=leads, filename="buy_import_export.csv")
    except Exception as ex:
        logger.error(f"[{trace_id}] export_buy_import_leads failed: {str(ex)}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)


@router.get(
    "/import/{import_id}",
    response_model=BuyLeadImportItem,
    status_code=status.HTTP_200_OK,
)
async def get_buy_import_lead_by_id(
    request: Request,
    import_id: UUID,
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> BuyLeadImportItem:
    logger.info(f"request: {request}, user: {current_user}, id:{import_id}")
    try:
        lead = await buy_service.get_import_lead_by_id(
            import_id, current_user.user_name, current_user.role_id
        )
        if not lead:
            logger.info(f"Not Found: {import_id}")
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


@router.post(
    "/{lead_id}/payment",
    response_model=Response,
    status_code=status.HTTP_201_CREATED,
)
async def create_lead_payment(
    request: Request,
    lead_id: int = Path(..., gt=0),
    lead_payment: CreateBuyLeadPayment = Body(..., example=example.BUY_LEAD_PAYMENT),
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(require_roles(settings.payment_role_ids)),
    trace_id: UUID = Depends(get_trace_id),
) -> Response:
    logger.info(f"request: {request}")
    try:
        payment_id = await buy_service.create_lead_payment(
            lead_payment=lead_payment.to_model(
                lead_id=lead_id,
                created_by=current_user.user_name,
            ),
            created_by=current_user.user_name,
        )
    except CreationError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.FAILED)
    except NotFound as ex:
        logger.error(f"Not Found error: {ex}")
        raise HTTPException(status.HTTP_404_NOT_FOUND, constant.NOTFOUND)
    except ValueError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.VALUEERROR)
    except Exception as ex:
        logger.error(f"[{trace_id}] create_lead failed: {str(ex)}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)
    return Response(id=payment_id, message=constant.CREATED)


@router.get(
    "/{lead_id}/payment/pdf",
    status_code=status.HTTP_200_OK,
)
async def download_lead_payment_pdf(
    request: Request,
    lead_id: int = Path(..., gt=0),
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(require_roles(settings.payment_role_ids)),
    trace_id: UUID = Depends(get_trace_id),
):
    logger.info(f"request: {request}, user: {current_user}, id:{lead_id}")
    try:
        payment_pdf = await buy_service.get_lead_payment_pdf(
            lead_id=lead_id,
            created_by=current_user.user_name,
            role_id=current_user.role_id,
        )
        if not payment_pdf:
            raise HTTPException(status.HTTP_404_NOT_FOUND, constant.NOTFOUND)

        filename, pdf_bytes = payment_pdf
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )
    except HTTPException:
        raise
    except ValueError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.VALUEERROR)
    except Exception as ex:
        logger.error(f"[{trace_id}] download_lead_payment_pdf failed: {str(ex)}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)


@router.post(
    "/lead/{lead_id}/evaluation",
    response_model=Response,
    status_code=201,
)
async def create_evaluation(
    request: Request,
    background_tasks: BackgroundTasks,
    lead_id: Annotated[int, Path(gt=0)],
    evaluation_data: Annotated[str, Form(...)],
    photos: Annotated[str, Form(...)],
    files: Annotated[
        list[UploadFile],
        File(
            ...,
            description="Upload evaluation images",
        ),
    ],
    remarks: Annotated[str, Form(...)],
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(
        require_roles(settings.evaluation_role_ids)
    ),
    trace_id: UUID = Depends(get_trace_id),
):

    logger.info(f"request: {request}, user: {current_user}, id:{lead_id}")
    try:
        lead = await buy_service.get_lead_by_id(lead_id)
        if not lead:
            logger.info(f"Not Found: {lead_id}")
            raise HTTPException(status.HTTP_404_NOT_FOUND, constant.NOTFOUND)

        evaluation_parameters = await validate_evaluation_parameters(
            evaluation_data=evaluation_data,
        )

        await buy_service.save_evaluation_parameters(
            lead_id=lead_id,
            remarks=remarks,
            evaluation_parameters=evaluation_parameters,
            created_by=current_user.user_name,
        )

        processed_files = await validate_photos(
            photos=photos,
            files=files,
        )

        background_tasks.add_task(
            buy_service.process_evaluation_photos,
            lead_id,
            processed_files,
            current_user.user_name,
        )

    except HTTPException as ex:
        logger.error(
            f"General HTTP exception [{trace_id}] \
                     Evaluation failed: {str(ex)}"
        )
        raise ex
    except CreationError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.FAILED)
    except ValueError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.VALUEERROR)
    except Exception as ex:
        logger.error(f"[{trace_id}] Evaluation failed: {str(ex)}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)
    return Response(id=lead_id, message=constant.REQUEST)


@router.post(
    "/lead/{lead_id}/stockin",
    response_model=Response,
    status_code=201,
)
async def create_stockin(
    request: Request,
    background_tasks: BackgroundTasks,
    lead_id: Annotated[int, Path(gt=0)],
    documents: Annotated[str, Form(...)],
    files: Annotated[
        list[UploadFile],
        File(
            ...,
            description="Upload stockin documents",
        ),
    ],
    remarks: Annotated[str, Form(...)],
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(require_roles(settings.payment_role_ids)),
    trace_id: UUID = Depends(get_trace_id),
):
    logger.info(f"request: {request}, user: {current_user}, id:{lead_id}")
    try:
        lead = await buy_service.get_lead_by_id(lead_id)
        if not lead:
            logger.info(f"Not Found: {lead_id}")
            raise HTTPException(status.HTTP_404_NOT_FOUND, constant.NOTFOUND)

        processed_documents = await validate_stockin_documents(
            documents=documents,
            files=files,
        )

        await buy_service.save_stockin(
            lead_id=lead_id,
            remarks=remarks,
            created_by=current_user.user_name,
        )

        background_tasks.add_task(
            buy_service.process_stockin_documents,
            lead_id,
            processed_documents,
            current_user.user_name,
        )

    except HTTPException as ex:
        logger.error(f"General HTTP exception [{trace_id}] Stockin failed: {str(ex)}")
        raise ex
    except CreationError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.FAILED)
    except ValueError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.VALUEERROR)
    except Exception as ex:
        logger.error(f"[{trace_id}] Stockin failed: {str(ex)}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)
    return Response(id=lead_id, message=constant.REQUEST)


@router.get(
    "/{lead_id}/evaluation/pdf",
    status_code=status.HTTP_200_OK,
)
async def download_lead_evaluation_pdf(
    request: Request,
    lead_id: int = Path(..., gt=0),
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(
        require_roles(
            list(
                set(
                    settings.admin_role_ids
                    + settings.evaluation_role_ids
                    + settings.payment_role_ids
                )
            )
        )
    ),
    trace_id: UUID = Depends(get_trace_id),
):
    logger.info(f"request: {request}, user: {current_user}, id:{lead_id}")
    try:
        evaluation_pdf = await buy_service.get_lead_evaluation_pdf(
            lead_id=lead_id,
            created_by=current_user.user_name,
            role_id=current_user.role_id,
        )
        if not evaluation_pdf:
            raise HTTPException(status.HTTP_404_NOT_FOUND, constant.NOTFOUND)

        filename, pdf_bytes = evaluation_pdf
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )
    except HTTPException:
        raise
    except ValueError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.VALUEERROR)
    except Exception as ex:
        logger.error(f"[{trace_id}] download_lead_evaluation_pdf failed: {str(ex)}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)


@router.post(
    "/target",
    response_model=Response,
    status_code=status.HTTP_201_CREATED,
)
async def create_buy_target(
    request: Request,
    target: CreateBuyTarget = Body(..., example=example.BUY_LEAD_TARGET),
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(require_roles(settings.admin_role_ids)),
    trace_id: UUID = Depends(get_trace_id),
) -> Response:
    logger.info(f"request: {request}, user: {current_user}, target: {target}")
    try:
        target_id = await buy_service.create_buy_target(
            target.to_model(), current_user.user_name
        )
    except CreationError as ex:
        logger.error(f"Creation error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.FAILED)
    except ValueError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.VALUEERROR)
    except Exception as ex:
        logger.error(f"[{trace_id}] create_buy_target failed: {str(ex)}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)
    return Response(id=target_id, message=constant.CREATED)


@router.get(
    "/target",
    response_model=BuyTargetList,
    status_code=status.HTTP_200_OK,
)
async def get_buy_target(
    request: Request,
    cursor: int | None = None,
    limit: int | None = None,
    search: str | None = None,
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(require_roles(settings.admin_role_ids)),
    trace_id: UUID = Depends(get_trace_id),
) -> BuyTargetList:
    logger.info(f"request: {request}, user: {current_user}")
    try:
        limit = normalize_limit(limit)
        targets = await buy_service.get_buy_target(
            cursor,
            limit,
            current_user.user_name,
            current_user.role_id,
            search,
        )
        total = await buy_service.get_total_buy_target(
            current_user.user_name, current_user.role_id, search
        )

        next_url = None
        if len(targets) == limit:
            last_id = targets[-1].id
            next_url = build_next_page_url(request, last_id, limit)

        return BuyTargetList(total=total, limit=limit, next=next_url, items=targets)
    except ValueError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.VALUEERROR)
    except Exception as ex:
        logger.error(f"Exception error: {ex}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)


@router.get(
    "/target/export",
    status_code=status.HTTP_200_OK,
)
async def export_buy_target(
    request: Request,
    search: str | None = None,
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(require_roles(settings.admin_role_ids)),
    trace_id: UUID = Depends(get_trace_id),
):
    logger.info(f"request: {request}, user: {current_user}")

    try:
        targets = buy_service.get_buy_target_export(
            current_user.user_name,
            current_user.role_id,
            search,
        )
        return stream_csv(rows=targets, filename="buy_lead_target_export.csv")
    except Exception as ex:
        logger.error(f"[{trace_id}] export_buy_targets failed: {str(ex)}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)


@router.get(
    "/target/{target_id}",
    response_model=BuyTargetItem,
    status_code=status.HTTP_200_OK,
)
async def get_buy_target_by_id(
    request: Request,
    target_id: int = Path(..., gt=0),
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(require_roles(settings.admin_role_ids)),
    trace_id: UUID = Depends(get_trace_id),
) -> BuyTargetItem:
    logger.info(f"request: {request}, user: {current_user}, target_id: {target_id}")
    try:
        target = await buy_service.get_buy_target_by_id(
            target_id, current_user.user_name, current_user.role_id
        )
        if not target:
            logger.info(f"Not Found: {target_id}")
            raise HTTPException(status.HTTP_404_NOT_FOUND, constant.NOTFOUND)
        return target
    except HTTPException:
        raise
    except ValueError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.VALUEERROR)
    except Exception as ex:
        logger.error(f"Exception error: {ex}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)


@router.put(
    "/target/{target_id}",
    response_model=Response,
    status_code=status.HTTP_200_OK,
)
async def update_buy_target(
    request: Request,
    target_id: int = Path(..., gt=0),
    target: UpdateBuyTarget = Body(..., example=example.UPDATE_BUY_LEAD_TARGET),
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(require_roles(settings.admin_role_ids)),
    trace_id: UUID = Depends(get_trace_id),
) -> Response:
    logger.info(
        f"request: {request}, user: {current_user}, \
            target_id: {target_id}, target: {target}"
    )

    try:
        await buy_service.update_buy_target(
            target_id, target.to_model(), current_user.user_name
        )

    except NotFound as ex:
        logger.error(f"Not Found error: {ex}")
        raise HTTPException(status.HTTP_404_NOT_FOUND, constant.NOTFOUND)
    except ValueError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.VALUEERROR)
    except Exception as ex:
        logger.error(f"[{trace_id}] update_buy_target failed: {str(ex)}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)

    return Response(id=target_id, message=constant.UPDATED)


@router.delete(
    "/target/{target_id}",
    response_model=Response,
    status_code=status.HTTP_200_OK,
)
async def remove_buy_target_by_id(
    request: Request,
    target_id: int = Path(..., gt=0),
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(require_roles(settings.admin_role_ids)),
    trace_id: UUID = Depends(get_trace_id),
) -> Response:
    logger.info(f"request: {request}, user: {current_user}, id:{id}")
    try:
        target = await buy_service.get_buy_target_by_id(
            target_id, current_user.user_name, current_user.role_id
        )
        if not target:
            logger.info(f"Not Found: {id}")
            raise HTTPException(status.HTTP_404_NOT_FOUND, constant.NOTFOUND)

        await buy_service.remove_buy_target(
            target_id, current_user.user_name, current_user.role_id
        )
        return Response(id=target_id, message=constant.REMOVED)
    except HTTPException:
        raise
    except ValueError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.VALUEERROR)
    except Exception as ex:
        logger.error(f"Exception error: {ex}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)


@router.patch(
    "/{lead_id}/sent/preprice",
    response_model=Response,
    status_code=status.HTTP_200_OK,
)
async def sent_lead_preprice(
    request: Request,
    lead_id: int = Path(..., gt=0),
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> Response:
    logger.info(f"request: {request}")
    try:
        lead_id = await buy_service.sent_lead_preprice(
            lead_id=lead_id,
            created_by=current_user.user_name,
        )

    except CreationError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.FAILED)
    except NotFound as ex:
        logger.error(f"Not Found error: {ex}")
        raise HTTPException(status.HTTP_404_NOT_FOUND, constant.NOTFOUND)
    except ValueError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.VALUEERROR)
    except Exception as ex:
        logger.error(f"[{trace_id}] sent_preprice_lead failed: {str(ex)}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)
    return Response(id=lead_id, message=constant.SENT)


@router.post(
    "/{lead_id}/provide/preprice",
    response_model=Response,
    status_code=status.HTTP_201_CREATED,
)
async def provide_lead_preprice(
    request: Request,
    lead_id: int = Path(..., gt=0),
    lead_preprice: ProvideBuyLeadPreprice = Body(
        ..., example=example.PROVIDE_BUY_LEAD_PREPRICE
    ),
    buy_service: BuyServiceInterface = Depends(deps.buy_service),
    current_user: AuthenticatedUser = Depends(
        require_roles(
            list(
                set(
                    settings.admin_role_ids
                    + settings.pricing_role_ids
                    + settings.payment_role_ids
                )
            )
        )
    ),
    trace_id: UUID = Depends(get_trace_id),
) -> Response:
    logger.info(f"request: {request}")
    try:
        preprice_id = await buy_service.provide_lead_preprice(
            lead_id=lead_id,
            lead_preprice=lead_preprice.to_model(),
            created_by=current_user.user_name,
        )

    except CreationError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.FAILED)
    except NotFound as ex:
        logger.error(f"Not Found error: {ex}")
        raise HTTPException(status.HTTP_404_NOT_FOUND, constant.NOTFOUND)
    except ValueError as ex:
        logger.error(f"ValueError error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.VALUEERROR)
    except Exception as ex:
        logger.error(f"[{trace_id}] create_lead failed: {str(ex)}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)
    return Response(id=preprice_id, message=constant.CREATED)
