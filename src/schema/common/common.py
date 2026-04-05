from common.schema_types import CamelBaseModel
from typing import List, Optional
from enum import Enum
from datetime import datetime

class LeadSourceItem(CamelBaseModel):
    id: int
    source: str
    created_at: datetime
    created_by: str


class LeadSourceList(CamelBaseModel):
    total: int
    limit: int
    next: Optional[str]
    items: List[LeadSourceItem]


class LeadSourceSortBy(str, Enum):
    id = "id"
    source = "source"


class MakeItem(CamelBaseModel):
    id: int
    make: str
    is_premium: bool
    created_at: datetime
    created_by: str


class MakeList(CamelBaseModel):
    total: int
    limit: int
    next: Optional[str]
    items: List[MakeItem]


class MakeSortBy(str, Enum):
    id = "id"
    make = "make"
    is_premium="is_premium"

class ModelItem(CamelBaseModel):
    id: int
    make_id: int
    make: str
    model: str
    created_at: datetime
    created_by: str


class ModelList(CamelBaseModel):
    total: int
    limit: int
    next: Optional[str]
    items: List[ModelItem]


class ModelSortBy(str, Enum):
    id = "id"
    make="make"
    model="model"


class BranchItem(CamelBaseModel):
    id: int
    branch: str
    created_at: datetime
    created_by: str


class BranchList(CamelBaseModel):
    total: int
    limit: int
    next: Optional[str]
    items: List[BranchItem]


class BranchSortBy(str, Enum):
    id = "id"
    branch="branch"

class YearItem(CamelBaseModel):
    year: int

class YearList(CamelBaseModel):
    total: int
    limit: int
    next: Optional[str]
    items: List[YearItem]


class BrokerItem(CamelBaseModel):
    id: int
    broker: str
    created_at: datetime
    created_by: str


class BrokerList(CamelBaseModel):
    total: int
    limit: int
    next: Optional[str]
    items: List[BrokerItem]


class BrokerSortBy(str, Enum):
    id = "id"
    booker="booker"


class StateItem(CamelBaseModel):
    id: int
    state: str
    created_at: datetime
    created_by: str


class StateList(CamelBaseModel):
    total: int
    limit: int
    next: Optional[str]
    items: List[StateItem]


class StateSortBy(str, Enum):
    id = "id"
    state = "state"

class CityItem(CamelBaseModel):
    id: int
    state_id: int
    state: str
    city: str
    created_at: datetime
    created_by: str


class CityList(CamelBaseModel):
    total: int
    limit: int
    next: Optional[str]
    items: List[CityItem]


class CitySortBy(str, Enum):
    id = "id"
    state="state"
    city="city"