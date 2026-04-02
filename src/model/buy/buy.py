from typing import Optional, List

from pydantic.dataclasses import dataclass

from api.schema_types import BuyMode, Color, FuelType


@dataclass
class BuyLead:
    branch: str
    mobile: str
    alternate_mobile: Optional[str]
    source: str
    mode: BuyMode
    customer_name: str
    make_id: int
    model_id: int
    fuel_type: FuelType
    year: int
    kms: int
    owner: str
    client_offer: int
    our_offer: int
    remarks: str
    broker_name: str | None = None
    variant: str | None = None
    color: Color | None = None
    telecaller: str | None = None
    executive: str | None = None
    lead_address: BuyLeadAddress | None = None
    created_by: str | None = None


@dataclass
class UpdateLead:
    branch: str
    alternate_mobile: Optional[str]
    source: str
    customer_name: str
    make_id: int
    model_id: int
    fuel_type: FuelType
    year: int
    kms: int
    owner: str
    client_offer: int
    our_offer: int
    remarks: str
    broker_name: str | None = None
    variant: str | None = None
    color: Color | None = None
    lead_address: BuyLeadAddress | None = None
    created_by: str | None = None
    

@dataclass
class BuyLeadAddress:
    address: str
    state: str
    city: str
    area: Optional[str]
    pincode: int | None = None

@dataclass
class BuyLeadFollowup:
    stage: str
    disposition: str
    calldate: str
    notes: Optional[str]


@dataclass
class AllocateLeadsRequest:
    lead_ids: List[int]
    telecaller: str | None = None
    executive: str | None = None
