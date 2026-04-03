from fastapi import APIRouter
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from common.utils import enum_to_dict_list
from api.deps import get_authenticated_user, get_trace_id
from api.common import deps

from api.schema_types import BuyMode, Color, FuelType, Owner, BuyStage, STAGE_DISPOSITION_MAP
from app.core.logging import logger
from api.schema_types import SortOrder, generate_time_slots
from common.cursor_pagination import build_next_page_url, normalize_limit
from services.common.common_service_interface import CommonServiceInterface

from auth.dto import AuthenticatedUser

from schema.common.common import (
    LeadSourceList,
    LeadSourceSortBy,
    MakeList,
    MakeSortBy,
    ModelList,
    ModelSortBy,
    BranchList,
    BranchSortBy,
    YearList,
    BrokerList,
    BrokerSortBy,
    StateList,
    StateSortBy,
    CityList,
    CitySortBy,
    )
router = APIRouter(prefix="/common", tags=["common"])

# region Enum
@router.get("/buy-mode")
def get_buy_mode():
    return enum_to_dict_list(BuyMode)


@router.get("/color")
def get_color():
    return enum_to_dict_list(Color)


@router.get("/fuel-type")
def get_fuel_type():
    return enum_to_dict_list(FuelType)

@router.get("/owner")
def get_owner():
    return enum_to_dict_list(Owner)

@router.get("/buy-stage")
def get_buy_stage():
    return enum_to_dict_list(BuyStage)

@router.get("/buy-stage/{stage}/disposition")
def get_buy_stage_disposition(stage: BuyStage):
    dispositon = STAGE_DISPOSITION_MAP.get(stage, [])
    return enum_to_dict_list(dispositon)

@router.get("/preferred-time")
async def get_preferred_time():
    return [{"value": t, "label": t} for t in generate_time_slots()]

# Optional: Single API for all enums
@router.get("/all")
def get_all_enums():
    return {
        "buyMode": enum_to_dict_list(BuyMode),
        "color": enum_to_dict_list(Color),
        "fuelType": enum_to_dict_list(FuelType),
        "owner": enum_to_dict_list(Owner),
        "buyStage": enum_to_dict_list(BuyStage),
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
    sort_by: LeadSourceSortBy = Query(LeadSourceSortBy.id, description="Field to sort by"),
    sort_order: SortOrder = Query(SortOrder.desc, description="Sort direction"),
    commmon_service: CommonServiceInterface = Depends(deps.common_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
) -> LeadSourceList:
    logger.info(f"request:{request},current_user:{current_user}")
    limit = normalize_limit(limit)
    source = await commmon_service.get_source(
        cursor, limit, search, sort_by.value, sort_order.value
    )
    total = await commmon_service.get_total_source(search)

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
    commmon_service: CommonServiceInterface = Depends(deps.common_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
) -> MakeList:
    logger.info(f"request:{request},current_user:{current_user}")
    limit = normalize_limit(limit)
    make = await commmon_service.get_make(
        cursor, limit, search, sort_by.value, sort_order.value
    )
    total = await commmon_service.get_total_make(search)

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
    commmon_service: CommonServiceInterface = Depends(deps.common_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
) -> ModelList:
    logger.info(f"request:{request},current_user:{current_user}")
    limit = normalize_limit(limit)
    model = await commmon_service.get_model(
        make_id=make_id,
        cursor=cursor, 
        limit=limit, 
        search=search, 
        sort_by=sort_by.value, 
        sort_order=sort_order.value
    )
    total = await commmon_service.get_total_model(make_id=make_id,search=search)

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
    commmon_service: CommonServiceInterface = Depends(deps.common_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
) -> BranchList:
    logger.info(f"request:{request},current_user:{current_user}")
    limit = normalize_limit(limit)
    branch = await commmon_service.get_branch(
        cursor, limit, search, sort_by.value, sort_order.value
    )
    total = await commmon_service.get_total_branch(search)

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
    commmon_service: CommonServiceInterface = Depends(deps.common_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
) -> BrokerList:
    logger.info(f"request:{request},current_user:{current_user}")
    limit = normalize_limit(limit)
    broker = await commmon_service.get_broker(
        cursor, limit, search, sort_by.value, sort_order.value
    )
    total = await commmon_service.get_total_broker(search)

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
    commmon_service: CommonServiceInterface = Depends(deps.common_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
) -> YearList:
    logger.info(f"request:{request},current_user:{current_user}")
    limit = normalize_limit(limit)
    year = await commmon_service.get_year(
        cursor, limit, search
    )
    total = await commmon_service.get_total_year(search)

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
    commmon_service: CommonServiceInterface = Depends(deps.common_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
) -> StateList:
    logger.info(f"request:{request},current_user:{current_user}")
    limit = normalize_limit(limit)
    state = await commmon_service.get_state(
        cursor, limit, search, sort_by.value, sort_order.value
    )
    total = await commmon_service.get_total_state(search)

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
    commmon_service: CommonServiceInterface = Depends(deps.common_service),
    current_user: AuthenticatedUser = Depends(get_authenticated_user),
) -> CityList:
    logger.info(f"request:{request},current_user:{current_user}")
    limit = normalize_limit(limit)
    city = await commmon_service.get_city(
        state_id=state_id,
        cursor=cursor, 
        limit=limit, 
        search=search, 
        sort_by=sort_by.value, 
        sort_order=sort_order.value
    )
    total = await commmon_service.get_total_city(state_id=state_id,search=search)

    next_url = None
    if len(city) == limit:
        last_id = city[-1].id
        next_url = build_next_page_url(request, last_id, limit)

    return CityList(total=total, limit=limit, next=next_url, items=city)

