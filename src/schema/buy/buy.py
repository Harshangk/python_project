from datetime import datetime
from enum import Enum
from typing import Annotated, List, Optional

from pydantic import Field, StringConstraints, field_validator

from api.buy.example import BUY_LEAD
from api.schema_types import BuyMode, CamelBaseModel, Color, FuelType
from model.buy import buy as BuyModel


class Response(CamelBaseModel):
    id: int
    message: str


class CreateBuyLead(CamelBaseModel):
    mobile: str
    alternate_mobile: str
    source: str
    mode: BuyMode
    broker_name: str = Field(..., min_length=1, max_length=255)
    customer_name: str = Field(..., min_length=1, max_length=255)
    make_id: int
    model_id: int
    variant: str = Field(..., min_length=1, max_length=255)
    color: Color
    fuel_type: FuelType
    year: Annotated[str, StringConstraints(pattern=r"^\d{4}$")]
    kms: int
    owner: str = Field(..., min_length=1, max_length=1)
    client_offer: int
    our_offer: int
    telecaller: str = Field(..., min_length=1, max_length=50)
    executive: str = Field(..., min_length=1, max_length=50)
    remarks: str = Field(..., min_length=1, max_length=500)

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
        )


class BuyLeadItem(CamelBaseModel):
    id: int
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
