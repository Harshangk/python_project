from datetime import datetime
from enum import Enum
from typing import Annotated, List, Optional
from uuid import UUID

from pydantic import (
    BeforeValidator,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

from api.buy.example import (
    BUY_LEAD,
    BUY_LEAD_ALLOCATION,
    BUY_LEAD_FOLLOWUP,
    UPDATE_LEAD,
)
from common.schema_types import BuyMode, CamelBaseModel, Color, FuelType
from model.buy import buy as BuyModel


def empty_to_none(v):
    return None if v == "" else v


class Response(CamelBaseModel):
    id: int | UUID
    message: str


class LeadAddress(CamelBaseModel):
    address: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=25)
    city: str = Field(..., min_length=1, max_length=25)
    area: str | None = Field(None, min_length=1, max_length=25)
    pincode: int | None = None


class CreateBuyLead(CamelBaseModel):
    branch: str
    mobile: str
    alternate_mobile: str | None = Field(None, max_length=15)
    source: str
    mode: BuyMode
    broker_name: str | None = Field(None, max_length=255)
    customer_name: str = Field(..., min_length=1, max_length=255)
    lead_address: LeadAddress | None = None
    make_id: int
    model_id: int
    variant: str | None = Field(None, max_length=255)
    color: Annotated[Color | None, BeforeValidator(empty_to_none)] = None
    fuel_type: FuelType
    year: Annotated[str, StringConstraints(pattern=r"^\d{4}$")]
    kms: int
    owner: str = Field(..., min_length=1, max_length=1)
    client_offer: int
    our_offer: int
    remarks: str = Field(..., min_length=1, max_length=500)
    telecaller: str | None = Field(None, max_length=50)
    executive: str | None = Field(None, max_length=50)

    @field_validator("mobile")
    def validate_mobile(cls, v):
        if not (10 <= len(v) <= 15):
            raise ValueError("Mobile number must be between 10 and 15 digits")
        if not v.isdigit():
            raise ValueError("Mobile must contain only digits")
        return v

    class config:
        schema_extra = {"example": BUY_LEAD}
        orm_mode = True

    def to_model(self) -> BuyModel.BuyLead:
        return BuyModel.BuyLead(
            branch=self.branch,
            mobile=self.mobile,
            alternate_mobile=self.alternate_mobile,
            source=self.source,
            mode=self.mode,
            broker_name=self.broker_name,
            customer_name=self.customer_name,
            make_id=self.make_id,
            model_id=self.model_id,
            variant=self.variant,
            color=self.color,
            fuel_type=self.fuel_type,
            year=self.year,
            kms=self.kms,
            owner=self.owner,
            client_offer=self.client_offer,
            our_offer=self.our_offer,
            telecaller=self.telecaller,
            executive=self.executive,
            remarks=self.remarks,
            lead_address=(
                BuyModel.BuyLeadAddress(
                    address=self.lead_address.address,
                    state=self.lead_address.state,
                    city=self.lead_address.city,
                    area=self.lead_address.area,
                    pincode=self.lead_address.pincode,
                )
                if self.lead_address
                else None
            ),
        )


class UpdateBuyLead(CamelBaseModel):
    branch: str
    alternate_mobile: str | None = Field(None, max_length=15)
    source: str
    broker_name: str | None = Field(None, max_length=255)
    customer_name: str = Field(..., min_length=1, max_length=255)
    lead_address: LeadAddress | None = None
    make_id: int
    model_id: int
    variant: str | None = Field(None, max_length=255)
    color: Annotated[Color | None, BeforeValidator(empty_to_none)] = None
    fuel_type: FuelType
    year: Annotated[str, StringConstraints(pattern=r"^\d{4}$")]
    kms: int
    owner: str = Field(..., min_length=1, max_length=1)
    client_offer: int
    our_offer: int
    remarks: str = Field(..., min_length=1, max_length=500)

    class config:
        schema_extra = {"example": UPDATE_LEAD}
        orm_mode = True

    def to_model(self) -> BuyModel.UpdateLead:
        return BuyModel.UpdateLead(
            branch=self.branch,
            alternate_mobile=self.alternate_mobile,
            source=self.source,
            broker_name=self.broker_name,
            customer_name=self.customer_name,
            make_id=self.make_id,
            model_id=self.model_id,
            variant=self.variant,
            color=self.color,
            fuel_type=self.fuel_type,
            year=self.year,
            kms=self.kms,
            owner=self.owner,
            client_offer=self.client_offer,
            our_offer=self.our_offer,
            remarks=self.remarks,
            lead_address=(
                BuyModel.BuyLeadAddress(
                    address=self.lead_address.address,
                    state=self.lead_address.state,
                    city=self.lead_address.city,
                    area=self.lead_address.area,
                    pincode=self.lead_address.pincode,
                )
                if self.lead_address
                else None
            ),
        )


class BuyLeadItem(CamelBaseModel):
    id: int
    branch: str
    mobile: str
    alternate_mobile: str | None = None
    source: str
    mode: BuyMode
    broker_name: str | None = None
    customer_name: str
    make_id: int
    model_id: int
    variant: str | None = None
    color: Color | None = None
    fuel_type: FuelType
    year: str
    kms: int
    owner: str
    client_offer: int
    our_offer: int
    status: str
    telecaller: str | None = None
    executive: str | None = None
    remarks: str
    allocated_at: datetime | None = None
    allocated_by: str | None = None
    created_at: datetime
    created_by: str
    make: str
    model: str
    lead_address: LeadAddress | None = None


class BuyLeadList(CamelBaseModel):
    total: int
    limit: int
    next: Optional[str]
    items: List[BuyLeadItem]


class BuyLeadSortBy(str, Enum):
    id = "id"
    mobile = "mobile"
    source = "source"
    mode = "mode"
    make_id = "make"
    model_id = "model"
    year = "year"
    kms = "kms"


class AllocateLeadsRequest(CamelBaseModel):
    lead_ids: List[int] = Field(..., min_length=1)
    telecaller: str | None = None
    executive: str | None = None

    @model_validator(mode="after")
    def check_at_least_one(self):
        if not self.telecaller and not self.executive:
            raise ValueError("Either telecaller or executive must be provided")
        return self

    class config:
        schema_extra = {"example": BUY_LEAD_ALLOCATION}
        orm_mode = True

    def to_model(self) -> BuyModel.AllocateLeadsRequest:
        return BuyModel.AllocateLeadsRequest(
            lead_ids=self.lead_ids,
            telecaller=self.telecaller,
            executive=self.executive,
        )


class LeadFollowup(CamelBaseModel):
    stage: str = Field(..., min_length=1, max_length=25)
    disposition: str = Field(..., min_length=1, max_length=50)
    calldate: datetime
    preferred_time: str | None = Field(None, max_length=20)
    notes: str = Field(..., min_length=1, max_length=500)

    @field_validator("calldate")
    def remove_timezone(cls, v):
        return v.replace(tzinfo=None) if v.tzinfo else v


class CreateBuyLeadFollowup(CamelBaseModel):
    branch: str
    customer_name: str = Field(..., min_length=1, max_length=255)
    alternate_mobile: str | None = Field(None, max_length=15)
    mode: BuyMode
    source: str
    broker_name: str | None = Field(None, max_length=255)
    lead_address: LeadAddress | None = None
    make_id: int
    model_id: int
    variant: str | None = Field(None, max_length=255)
    color: Annotated[Color | None, BeforeValidator(empty_to_none)] = None
    fuel_type: FuelType
    year: Annotated[str, StringConstraints(pattern=r"^\d{4}$")]
    kms: int
    owner: str = Field(..., min_length=1, max_length=1)
    client_offer: int
    our_offer: int
    telecaller: str | None = Field(None, max_length=50)
    executive: str | None = Field(None, max_length=50)
    lead_followup: LeadFollowup

    class config:
        schema_extra = {"example": BUY_LEAD_FOLLOWUP}
        orm_mode = True

    def to_model(self) -> BuyModel.BuyLeadFollowup:
        return BuyModel.BuyLeadFollowup(
            branch=self.branch,
            customer_name=self.customer_name,
            alternate_mobile=self.alternate_mobile,
            mode=self.mode,
            source=self.source,
            broker_name=self.broker_name,
            make_id=self.make_id,
            model_id=self.model_id,
            variant=self.variant,
            color=self.color,
            fuel_type=self.fuel_type,
            year=self.year,
            kms=self.kms,
            owner=self.owner,
            client_offer=self.client_offer,
            our_offer=self.our_offer,
            telecaller=self.telecaller,
            executive=self.executive,
            lead_address=(
                BuyModel.BuyLeadAddress(
                    address=self.lead_address.address,
                    state=self.lead_address.state,
                    city=self.lead_address.city,
                    area=self.lead_address.area,
                    pincode=self.lead_address.pincode,
                )
                if self.lead_address
                else None
            ),
            lead_followup=(
                BuyModel._BuyLeadFollowup(
                    stage=self.lead_followup.stage,
                    disposition=self.lead_followup.disposition,
                    calldate=self.lead_followup.calldate,
                    preferred_time=self.lead_followup.preferred_time,
                    notes=self.lead_followup.notes,
                )
                if self.lead_followup
                else None
            ),
        )


class BuyLeadFollowupItem(CamelBaseModel):
    id: int
    status: str
    mobile: str
    customer_name: str
    lead_followup: LeadFollowup
    branch: str
    source: str
    mode: BuyMode
    make: str
    model: str
    variant: str | None = None
    color: Color | None = None
    fuel_type: FuelType
    year: str
    kms: int
    owner: str
    client_offer: int
    our_offer: int
    telecaller: str | None = None
    executive: str | None = None
    alternate_mobile: str | None = None
    broker_name: str | None = None
    allocated_at: datetime | None = None
    allocated_by: str | None = None
    created_at: datetime
    created_by: str
    followup_created_at: datetime
    followup_created_by: str


class BuyLeadFollowupList(CamelBaseModel):
    total: int
    limit: int
    next: Optional[str]
    items: List[BuyLeadFollowupItem]


class BuyLeadFollowupDetail(CamelBaseModel):
    id: int
    status: str
    mobile: str
    customer_name: str
    lead_followup: LeadFollowup
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
    lead_address: LeadAddress | None = None
