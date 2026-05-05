from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse

from api.common import deps
from api.deps import get_authenticated_user, get_trace_id
from app import constant
from app.core.logging import logger
from auth.dto import AuthenticatedUser
from common.cursor_pagination import build_next_page_url, normalize_limit
from common.schema_types import (
    STAGE_DISPOSITION_MAP,
    Bucket,
    BuyMode,
    BuyStage,
    Category,
    Color,
    CommonFieldStatus,
    FuelType,
    InsuranceType,
    MemoPaid,
    Months,
    Owner,
    SortOrder,
    Transmission,
    generate_time_slots,
)
from common.utils import enum_to_dict_list
from schema.common.common import (
    BankList,
    BankSortBy,
    BranchList,
    BranchSortBy,
    BrokerList,
    BrokerSortBy,
    CityList,
    CitySortBy,
    InsuranceCompanyList,
    InsuranceCompanySortBy,
    LeadSourceList,
    LeadSourceSortBy,
    MakeList,
    MakeSortBy,
    ModelList,
    ModelSortBy,
    StateList,
    StateSortBy,
    YearList,
)
from services.common.common_service_interface import CommonServiceInterface

router = APIRouter(prefix="/common", tags=["common"])


# region Enum
@router.get("/buy-mode")
def get_buy_mode(trace_id: UUID = Depends(get_trace_id)):
    return enum_to_dict_list(BuyMode)


@router.get("/color")
def get_color(trace_id: UUID = Depends(get_trace_id)):
    return enum_to_dict_list(Color)


@router.get("/fuel-type")
def get_fuel_type(trace_id: UUID = Depends(get_trace_id)):
    return enum_to_dict_list(FuelType)


@router.get("/owner")
def get_owner(trace_id: UUID = Depends(get_trace_id)):
    return enum_to_dict_list(Owner)


@router.get("/category")
def get_category(trace_id: UUID = Depends(get_trace_id)):
    return enum_to_dict_list(Category)


@router.get("/months")
def get_months(trace_id: UUID = Depends(get_trace_id)):
    return enum_to_dict_list(Months)


@router.get("/common-field-status")
def get_common_field_status(trace_id: UUID = Depends(get_trace_id)):
    return enum_to_dict_list(CommonFieldStatus)


@router.get("/transmission")
def get_transmission(trace_id: UUID = Depends(get_trace_id)):
    return enum_to_dict_list(Transmission)


@router.get("/insurance-type")
def get_insurance_type(trace_id: UUID = Depends(get_trace_id)):
    return enum_to_dict_list(InsuranceType)


@router.get("/memo-paid")
def get_memo_paid(trace_id: UUID = Depends(get_trace_id)):
    return enum_to_dict_list(MemoPaid)


@router.get("/buy-stage")
def get_buy_stage(trace_id: UUID = Depends(get_trace_id)):
    return [
        {"value": item.value, "label": item.value}
        for item in BuyStage
        if item != BuyStage.Fresh
    ]


@router.get("/buy-stage/{stage}/disposition")
def get_buy_stage_disposition(stage: BuyStage, trace_id: UUID = Depends(get_trace_id)):
    disposition = STAGE_DISPOSITION_MAP.get(stage, [])
    return enum_to_dict_list(disposition)


@router.get("/preferred-time")
async def get_preferred_time(trace_id: UUID = Depends(get_trace_id)):
    return [{"value": t, "label": t} for t in generate_time_slots()]


@router.get("/bucket")
def get_bucket_name(trace_id: UUID = Depends(get_trace_id)):
    return enum_to_dict_list(Bucket)


# Optional: Single API for all enums
@router.get("/all")
def get_all_enums(trace_id: UUID = Depends(get_trace_id)):
    return {
        "buyMode": enum_to_dict_list(BuyMode),
        "color": enum_to_dict_list(Color),
        "fuelType": enum_to_dict_list(FuelType),
        "owner": enum_to_dict_list(Owner),
        "buyStage": enum_to_dict_list(BuyStage),
        "bucket": enum_to_dict_list(Bucket),
        "category": enum_to_dict_list(Category),
        "months": enum_to_dict_list(Months),
        "transmission": enum_to_dict_list(Transmission),
        "insuranceType": enum_to_dict_list(InsuranceType),
        "memoPaid": enum_to_dict_list(MemoPaid),
        "commonFieldStatus": enum_to_dict_list(CommonFieldStatus),
    }


# endregion Enum


@router.get(
    "/lead-source",
    response_model=LeadSourceList,
    status_code=status.HTTP_200_OK,
)
async def get_lead_source(
    request: Request,
    cursor: int | None = None,
    limit: int | None = None,
    search: str | None = None,
    sort_by: LeadSourceSortBy = Query(
        LeadSourceSortBy.id, description="Field to sort by"
    ),
    sort_order: SortOrder = Query(SortOrder.desc, description="Sort direction"),
    common_service: CommonServiceInterface = Depends(deps.common_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> LeadSourceList:
    logger.info(f"request:{request},current_user:{current_user}")
    limit = normalize_limit(limit)
    source = await common_service.get_source(
        cursor, limit, search, sort_by.value, sort_order.value
    )
    total = await common_service.get_total_source(search)

    next_url = None
    if len(source) == limit:
        last_id = source[-1].id
        next_url = build_next_page_url(request, last_id, limit)

    return LeadSourceList(total=total, limit=limit, next=next_url, items=source)


@router.get(
    "/make",
    response_model=MakeList,
    status_code=status.HTTP_200_OK,
)
async def get_make(
    request: Request,
    cursor: int | None = None,
    limit: int | None = None,
    search: str | None = None,
    sort_by: MakeSortBy = Query(MakeSortBy.id, description="Field to sort by"),
    sort_order: SortOrder = Query(SortOrder.desc, description="Sort direction"),
    common_service: CommonServiceInterface = Depends(deps.common_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> MakeList:
    logger.info(f"request:{request},current_user:{current_user}")
    limit = normalize_limit(limit)
    make = await common_service.get_make(
        cursor, limit, search, sort_by.value, sort_order.value
    )
    total = await common_service.get_total_make(search)

    next_url = None
    if len(make) == limit:
        last_id = make[-1].id
        next_url = build_next_page_url(request, last_id, limit)

    return MakeList(total=total, limit=limit, next=next_url, items=make)


@router.get(
    "/model",
    response_model=ModelList,
    status_code=status.HTTP_200_OK,
)
async def get_model(
    request: Request,
    make_id: int | None = None,
    cursor: int | None = None,
    limit: int | None = None,
    search: str | None = None,
    sort_by: ModelSortBy = Query(ModelSortBy.id, description="Field to sort by"),
    sort_order: SortOrder = Query(SortOrder.desc, description="Sort direction"),
    common_service: CommonServiceInterface = Depends(deps.common_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> ModelList:
    logger.info(f"request:{request},current_user:{current_user}")
    limit = normalize_limit(limit)
    model = await common_service.get_model(
        make_id=make_id,
        cursor=cursor,
        limit=limit,
        search=search,
        sort_by=sort_by.value,
        sort_order=sort_order.value,
    )
    total = await common_service.get_total_model(make_id=make_id, search=search)

    next_url = None
    if len(model) == limit:
        last_id = model[-1].id
        next_url = build_next_page_url(request, last_id, limit)

    return ModelList(total=total, limit=limit, next=next_url, items=model)


@router.get(
    "/branch",
    response_model=BranchList,
    status_code=status.HTTP_200_OK,
)
async def get_branch(
    request: Request,
    cursor: int | None = None,
    limit: int | None = None,
    search: str | None = None,
    sort_by: BranchSortBy = Query(BranchSortBy.id, description="Field to sort by"),
    sort_order: SortOrder = Query(SortOrder.desc, description="Sort direction"),
    common_service: CommonServiceInterface = Depends(deps.common_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> BranchList:
    logger.info(f"request:{request},current_user:{current_user}")
    limit = normalize_limit(limit)
    branch = await common_service.get_branch(
        cursor, limit, search, sort_by.value, sort_order.value
    )
    total = await common_service.get_total_branch(search)

    next_url = None
    if len(branch) == limit:
        last_id = branch[-1].id
        next_url = build_next_page_url(request, last_id, limit)

    return BranchList(total=total, limit=limit, next=next_url, items=branch)


@router.get(
    "/broker",
    response_model=BrokerList,
    status_code=status.HTTP_200_OK,
)
async def get_broker(
    request: Request,
    cursor: int | None = None,
    limit: int | None = None,
    search: str | None = None,
    sort_by: BrokerSortBy = Query(BrokerSortBy.id, description="Field to sort by"),
    sort_order: SortOrder = Query(SortOrder.desc, description="Sort direction"),
    common_service: CommonServiceInterface = Depends(deps.common_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> BrokerList:
    logger.info(f"request:{request},current_user:{current_user}")
    limit = normalize_limit(limit)
    broker = await common_service.get_broker(
        cursor, limit, search, sort_by.value, sort_order.value
    )
    total = await common_service.get_total_broker(search)

    next_url = None
    if len(broker) == limit:
        last_id = broker[-1].id
        next_url = build_next_page_url(request, last_id, limit)

    return BrokerList(total=total, limit=limit, next=next_url, items=broker)


@router.get(
    "/year",
    response_model=YearList,
    status_code=status.HTTP_200_OK,
)
async def get_year(
    request: Request,
    cursor: int | None = None,
    limit: int | None = None,
    search: str | None = None,
    common_service: CommonServiceInterface = Depends(deps.common_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> YearList:
    logger.info(f"request:{request},current_user:{current_user}")
    limit = normalize_limit(limit)
    year = await common_service.get_year(cursor, limit, search)
    total = await common_service.get_total_year(search)

    next_url = None
    if len(year) == limit:
        last_id = year[-1].id
        next_url = build_next_page_url(request, last_id, limit)

    return YearList(total=total, limit=limit, next=next_url, items=year)


@router.get(
    "/state",
    response_model=StateList,
    status_code=status.HTTP_200_OK,
)
async def get_state(
    request: Request,
    cursor: int | None = None,
    limit: int | None = None,
    search: str | None = None,
    sort_by: StateSortBy = Query(StateSortBy.id, description="Field to sort by"),
    sort_order: SortOrder = Query(SortOrder.desc, description="Sort direction"),
    common_service: CommonServiceInterface = Depends(deps.common_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> StateList:
    logger.info(f"request:{request},current_user:{current_user}")
    limit = normalize_limit(limit)
    state = await common_service.get_state(
        cursor, limit, search, sort_by.value, sort_order.value
    )
    total = await common_service.get_total_state(search)

    next_url = None
    if len(state) == limit:
        last_id = state[-1].id
        next_url = build_next_page_url(request, last_id, limit)

    return StateList(total=total, limit=limit, next=next_url, items=state)


@router.get(
    "/city",
    response_model=CityList,
    status_code=status.HTTP_200_OK,
)
async def get_city(
    request: Request,
    state_id: int | None = None,
    cursor: int | None = None,
    limit: int | None = None,
    search: str | None = None,
    sort_by: CitySortBy = Query(CitySortBy.id, description="Field to sort by"),
    sort_order: SortOrder = Query(SortOrder.desc, description="Sort direction"),
    common_service: CommonServiceInterface = Depends(deps.common_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> CityList:
    logger.info(f"request:{request},current_user:{current_user}")
    limit = normalize_limit(limit)
    city = await common_service.get_city(
        state_id=state_id,
        cursor=cursor,
        limit=limit,
        search=search,
        sort_by=sort_by.value,
        sort_order=sort_order.value,
    )
    total = await common_service.get_total_city(state_id=state_id, search=search)

    next_url = None
    if len(city) == limit:
        last_id = city[-1].id
        next_url = build_next_page_url(request, last_id, limit)

    return CityList(total=total, limit=limit, next=next_url, items=city)


@router.get(
    "/bank",
    response_model=BankList,
    status_code=status.HTTP_200_OK,
)
async def get_bank(
    request: Request,
    cursor: int | None = None,
    limit: int | None = None,
    search: str | None = None,
    sort_by: BankSortBy = Query(BankSortBy.id, description="Field to sort by"),
    sort_order: SortOrder = Query(SortOrder.desc, description="Sort direction"),
    common_service: CommonServiceInterface = Depends(deps.common_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> BankList:
    logger.info(f"request:{request},current_user:{current_user}")
    limit = normalize_limit(limit)
    bank = await common_service.get_bank(
        cursor, limit, search, sort_by.value, sort_order.value
    )
    total = await common_service.get_total_bank(search)

    next_url = None
    if len(bank) == limit:
        last_id = bank[-1].id
        next_url = build_next_page_url(request, last_id, limit)

    return BankList(total=total, limit=limit, next=next_url, items=bank)


@router.get(
    "/insurance-company",
    response_model=InsuranceCompanyList,
    status_code=status.HTTP_200_OK,
)
async def get_insurance_company(
    request: Request,
    cursor: int | None = None,
    limit: int | None = None,
    search: str | None = None,
    sort_by: InsuranceCompanySortBy = Query(
        InsuranceCompanySortBy.id, description="Field to sort by"
    ),
    sort_order: SortOrder = Query(SortOrder.desc, description="Sort direction"),
    common_service: CommonServiceInterface = Depends(deps.common_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
) -> InsuranceCompanyList:
    logger.info(f"request:{request},current_user:{current_user}")
    limit = normalize_limit(limit)
    insurance_company = await common_service.get_insurance_company(
        cursor, limit, search, sort_by.value, sort_order.value
    )
    total = await common_service.get_total_insurance_company(search)

    next_url = None
    if len(insurance_company) == limit:
        last_id = insurance_company[-1].id
        next_url = build_next_page_url(request, last_id, limit)

    return InsuranceCompanyList(
        total=total, limit=limit, next=next_url, items=insurance_company
    )


@router.get("/import/{s3_key:path}/download")
async def download_import_file(
    request: Request,
    s3_key: str,
    bucket: Bucket,
    common_service: CommonServiceInterface = Depends(deps.common_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
    trace_id: UUID = Depends(get_trace_id),
):
    try:
        logger.info(
            f"request:{request},current_user:{current_user},bucket:{bucket.value}"
        )

        file_obj, s3_key = await common_service.download_s3_file(s3_key, bucket.value)
        filename = s3_key.split("/")[-1]

        return StreamingResponse(
            file_obj,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except ValueError as ex:
        logger.error(f"Validation error: {ex}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, constant.VALUEERROR)
    except Exception as ex:
        logger.error(f"Exception error: {ex}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, constant.EXCEPTION)
