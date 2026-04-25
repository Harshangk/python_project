from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic.dataclasses import dataclass

from common.schema_types import BuyMode, BuyStatus, Color, FileStatus, FuelType


@dataclass
class BuyLeadAddress:
    address: str
    state: str
    city: str
    area: str | None = None
    pincode: int | None = None


@dataclass
class BuyLead:
    branch: str
    mobile: str
    source: str
    mode: BuyMode
    customer_name: str
    make_id: int
    model_id: int
    fuel_type: FuelType
    year: str
    kms: int
    owner: str
    client_offer: int
    our_offer: int
    remarks: str
    status: BuyStatus
    alternate_mobile: str | None = None
    broker_name: str | None = None
    variant: str | None = None
    color: Color | None = None
    telecaller: str | None = None
    executive: str | None = None
    lead_address: BuyLeadAddress | None = None
    created_by: str | None = None
    import_id: UUID | None = None


@dataclass
class UpdateLead:
    branch: str
    alternate_mobile: Optional[str]
    source: str
    customer_name: str
    make_id: int
    model_id: int
    fuel_type: FuelType
    year: str
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
class _BuyLeadFollowup:
    stage: str
    disposition: str
    notes: str
    calldate: datetime | None = None
    preferred_time: str | None = None


@dataclass
class BuyLeadFollowup:
    branch: str
    customer_name: str
    alternate_mobile: Optional[str]
    mode: BuyMode
    source: str
    make_id: int
    model_id: int
    fuel_type: FuelType
    year: str
    kms: int
    owner: str
    client_offer: int
    our_offer: int
    lead_followup: _BuyLeadFollowup
    broker_name: str | None = None
    variant: str | None = None
    color: Color | None = None
    telecaller: str | None = None
    executive: str | None = None
    lead_address: BuyLeadAddress | None = None
    created_by: str | None = None


@dataclass
class BuyLeadFollowupDetail:
    id: int
    status: str
    mobile: str
    customer_name: str
    lead_followup: _BuyLeadFollowup
    branch: str
    source: str
    mode: BuyMode
    make_id: int
    model_id: int
    fuel_type: FuelType
    year: str
    kms: int
    owner: str
    client_offer: int
    our_offer: int
    remarks: str
    allocated_at: datetime
    allocated_by: str
    created_at: datetime
    created_by: str
    followup_created_at: datetime
    followup_created_by: str
    variant: str | None = None
    color: Color | None = None
    telecaller: str | None = None
    executive: str | None = None
    alternate_mobile: str | None = None
    broker_name: str | None = None
    lead_address: BuyLeadAddress | None = None


@dataclass
class AllocateLeadsRequest:
    lead_ids: List[int]
    telecaller: str | None = None
    executive: str | None = None


@dataclass
class BuyLeadFile:
    s3_key: str
    file_status: FileStatus
    file_uuid: UUID
    processed_records: int
    error_records: int
    created_at: datetime
    created_by: str
    error_s3_key: str | None = None
