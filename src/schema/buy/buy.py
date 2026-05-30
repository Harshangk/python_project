from datetime import datetime
from decimal import Decimal
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
    BUY_LEAD_PAYMENT,
    BUY_LEAD_PREPRICE,
    BUY_LEAD_TARGET,
    UPDATE_LEAD,
)
from app.constant import BROKERINVALID, SOURCEINVALID
from common.schema_types import (
    BuyMode,
    CamelBaseModel,
    Category,
    Color,
    CommonFieldStatus,
    FileStatus,
    FuelType,
    InsuranceType,
    MemoPaid,
    Months,
    Transmission,
    validate_mobile,
)
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
    category: Category
    customer_name: str = Field(..., min_length=1, max_length=255)
    owner_name: str = Field(None, min_length=1, max_length=255)
    payment_name: str = Field(None, min_length=1, max_length=255)
    lead_address: LeadAddress | None = None
    make_id: int
    model_id: int
    variant: str | None = Field(None, max_length=255)
    color: Annotated[Color | None, BeforeValidator(empty_to_none)] = None
    fuel_type: FuelType
    mfg_month: Months
    mfg_year: Annotated[str, StringConstraints(pattern=r"^\d{4}$")]
    kms: int
    owner: str = Field(..., min_length=1, max_length=1)
    client_offer: int
    our_offer: int
    remarks: str = Field(..., min_length=1, max_length=500)
    telecaller: str | None = Field(None, max_length=50)
    executive: str | None = Field(None, max_length=50)

    @field_validator("mobile")
    def validate_mobile(cls, v):
        return validate_mobile(v)

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
            category=self.category,
            customer_name=self.customer_name,
            owner_name=self.owner_name,
            payment_name=self.payment_name,
            make_id=self.make_id,
            model_id=self.model_id,
            variant=self.variant,
            color=self.color,
            fuel_type=self.fuel_type,
            mfg_month=self.mfg_month,
            mfg_year=self.mfg_year,
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
    mfg_year: Annotated[str, StringConstraints(pattern=r"^\d{4}$")]
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
            mfg_year=self.mfg_year,
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


class LeadFollowup(CamelBaseModel):
    stage: str = Field(..., min_length=1, max_length=25)
    disposition: str = Field(..., min_length=1, max_length=50)
    calldate: datetime | None = None
    preferred_time: str | None = Field(None, max_length=20)
    notes: str = Field(..., min_length=1, max_length=500)

    @field_validator("calldate")
    def remove_timezone(cls, v):
        if v is None:
            return None
        return v.replace(tzinfo=None) if v.tzinfo else v


class BuyLeadItem(CamelBaseModel):
    id: int
    status: str
    mobile: str
    customer_name: str
    owner_name: str
    payment_name: str
    lead_followup: LeadFollowup | None = None
    branch: str
    source: str
    mode: BuyMode
    category: Category
    make_id: int
    make: str
    model_id: int
    model: str
    variant: str | None = None
    color: Color | None = None
    fuel_type: FuelType
    mfg_year: str
    kms: int
    owner: str
    client_offer: int
    our_offer: int
    created_at: datetime
    created_by: str
    remarks: str
    telecaller: str | None = None
    executive: str | None = None
    alternate_mobile: str | None = None
    broker_name: str | None = None
    allocated_at: datetime | None = None
    allocated_by: str | None = None
    followup_created_at: datetime | None = None
    followup_created_by: str | None = None
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
    mfg_year = "mfg_year"
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
    mfg_year: Annotated[str, StringConstraints(pattern=r"^\d{4}$")]
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
            mfg_year=self.mfg_year,
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
    mfg_year: str
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
    lead_address: LeadAddress | None = None


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
    mfg_year: str
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


class ImportBuyLeadRequest(CamelBaseModel):
    source: str = Field(..., max_length=50)
    broker_name: str | None = Field(None, max_length=255)

    @field_validator("source")
    @classmethod
    def validate_source_not_empty(cls, v: str):
        if not v.strip():
            raise ValueError(SOURCEINVALID)
        return v.strip()

    @field_validator("broker_name")
    @classmethod
    def validate_broker_name(cls, v):
        if v:
            return v.strip()
        return v

    @model_validator(mode="after")
    def validate_broker_requirement(self):
        if self.source.strip().lower() == "broker" and not self.broker_name:
            raise ValueError(BROKERINVALID)
        if self.source.strip().lower() != "broker":
            self.broker_name = None
        return self


class BuyLeadImportItem(CamelBaseModel):
    id: int
    s3_key: str
    file_status: FileStatus
    file_uuid: UUID
    processed_records: int
    error_records: int
    created_at: datetime
    created_by: str
    error_s3_key: str | None = None


class BuyLeadImportList(CamelBaseModel):
    total: int
    limit: int
    next: Optional[str]
    items: List[BuyLeadImportItem]


class LeadVehicle(CamelBaseModel):
    registration_no: str = Field(..., min_length=1, max_length=12)
    transmission: Transmission
    cubic_capacity: int | None = 0
    chassis_no: str = Field(None, min_length=1, max_length=50)
    engine_no: str = Field(None, min_length=1, max_length=50)
    push_button: CommonFieldStatus | None = None
    company_invoice: CommonFieldStatus | None = None
    noc: CommonFieldStatus | None = None
    reg_month: Months | None = None
    reg_year: Annotated[str, StringConstraints(pattern=r"^\d{4}$")]
    euro: str = Field(None, min_length=1, max_length=4)
    rc_book: CommonFieldStatus | None = None
    second_key: CommonFieldStatus | None = None
    hypo: CommonFieldStatus | None = None
    hypo_bank: str = Field(None, min_length=1, max_length=255)
    service_record: CommonFieldStatus | None = None
    puc: CommonFieldStatus | None = None
    memo: CommonFieldStatus | None = None
    memo_amount: Decimal = Decimal("0.00")
    memo_paid: MemoPaid | None = None
    mv_tax: Decimal = Decimal("0.00")
    rma: str = Field(None, min_length=1, max_length=8)
    taxi_private: str = Field(None, min_length=1, max_length=8)
    other_noc: str = Field(None, min_length=1, max_length=8)
    blacklist: str = Field(None, min_length=1, max_length=8)
    rto_status: str = Field(None, min_length=1, max_length=8)


class LeadVehicleInsurance(CamelBaseModel):
    online_insurance: CommonFieldStatus | None = None
    insurance_type: InsuranceType | None = None
    cp_zd_company: str = Field(None, min_length=1, max_length=255)
    tp_company: str = Field(None, min_length=1, max_length=255)
    cp_zd_date: datetime | None = None
    tp_date: datetime | None = None
    idv: Decimal = Decimal("0.00")
    ncb: Decimal = Decimal("0.00")
    premium: Decimal = Decimal("0.00")


class CreateBuyLeadPayment(CamelBaseModel):
    refurb_cost: Decimal = Decimal("0.00")
    deal: Decimal = Decimal("0.00")
    service_charge: Decimal = Decimal("0.00")
    tcs: Decimal = Decimal("0.00")
    gst: Decimal = Decimal("0.00")
    tax: Decimal = Decimal("0.00")
    rcd: Decimal = Decimal("0.00")
    commission: Decimal = Decimal("0.00")
    deal_with_commission: Decimal = Decimal("0.00")
    deal_without_commission: Decimal = Decimal("0.00")
    token: Decimal = Decimal("0.00")
    cash: Decimal = Decimal("0.00")
    loan: Decimal = Decimal("0.00")
    less: Decimal = Decimal("0.00")
    hold: Decimal = Decimal("0.00")
    ch_rtgs: Decimal = Decimal("0.00")
    total_payble: Decimal = Decimal("0.00")
    remarks: str = Field(..., min_length=1, max_length=500)
    lead_vehicle: LeadVehicle | None = None
    lead_vehicle_insurance: LeadVehicleInsurance | None = None

    class config:
        schema_extra = {"example": BUY_LEAD_PAYMENT}
        orm_mode = True

    def to_model(self, lead_id: int, created_by: str) -> BuyModel.BuyLeadPayment:
        return BuyModel.BuyLeadPayment(
            buylead_id=lead_id,
            refurb_cost=self.refurb_cost,
            deal=self.deal,
            service_charge=self.service_charge,
            tcs=self.tcs,
            gst=self.gst,
            tax=self.tax,
            rcd=self.rcd,
            commission=self.commission,
            deal_with_commission=self.deal_with_commission,
            deal_without_commission=self.deal_without_commission,
            token=self.token,
            cash=self.cash,
            loan=self.loan,
            less=self.less,
            hold=self.hold,
            ch_rtgs=self.ch_rtgs,
            total_payble=self.total_payble,
            remarks=self.remarks,
            created_by=created_by,
            lead_vehicle=(
                BuyModel.BuyLeadVehicle(
                    buylead_id=lead_id,
                    registration_no=self.lead_vehicle.registration_no,
                    transmission=self.lead_vehicle.transmission,
                    cubic_capacity=self.lead_vehicle.cubic_capacity,
                    chassis_no=self.lead_vehicle.chassis_no,
                    engine_no=self.lead_vehicle.engine_no,
                    push_button=self.lead_vehicle.push_button,
                    company_invoice=self.lead_vehicle.company_invoice,
                    noc=self.lead_vehicle.noc,
                    reg_month=self.lead_vehicle.reg_month,
                    reg_year=self.lead_vehicle.reg_year,
                    euro=self.lead_vehicle.euro,
                    rc_book=self.lead_vehicle.rc_book,
                    second_key=self.lead_vehicle.second_key,
                    hypo=self.lead_vehicle.hypo,
                    hypo_bank=self.lead_vehicle.hypo_bank,
                    service_record=self.lead_vehicle.service_record,
                    puc=self.lead_vehicle.puc,
                    memo=self.lead_vehicle.memo,
                    memo_amount=self.lead_vehicle.memo_amount,
                    memo_paid=self.lead_vehicle.memo_paid,
                    mv_tax=self.lead_vehicle.mv_tax,
                    rma=self.lead_vehicle.rma,
                    taxi_private=self.lead_vehicle.taxi_private,
                    other_noc=self.lead_vehicle.other_noc,
                    blacklist=self.lead_vehicle.blacklist,
                    rto_status=self.lead_vehicle.rto_status,
                )
                if self.lead_vehicle
                else None
            ),
            lead_vehicle_insurance=(
                BuyModel.BuyLeadVehicleInsurance(
                    buylead_id=lead_id,
                    online_insurance=self.lead_vehicle_insurance.online_insurance,
                    insurance_type=self.lead_vehicle_insurance.insurance_type,
                    cp_zd_company=self.lead_vehicle_insurance.cp_zd_company,
                    tp_company=self.lead_vehicle_insurance.tp_company,
                    cp_zd_date=self.lead_vehicle_insurance.cp_zd_date,
                    tp_date=self.lead_vehicle_insurance.tp_date,
                    idv=self.lead_vehicle_insurance.idv,
                    ncb=self.lead_vehicle_insurance.ncb,
                    premium=self.lead_vehicle_insurance.premium,
                )
                if self.lead_vehicle_insurance
                else None
            ),
        )


class CreateBuyTarget(CamelBaseModel):
    user_name: str = Field(..., min_length=1, max_length=50)
    month: Months
    year: Annotated[str, StringConstraints(pattern=r"^\d{4}$")]
    normal: int
    premium: int
    total: int

    class config:
        schema_extra = {"example": BUY_LEAD_TARGET}
        orm_mode = True

    def to_model(self) -> BuyModel.BuyLeadTarget:
        return BuyModel.BuyLeadTarget(
            user_name=self.user_name,
            month=self.month,
            year=self.year,
            normal=self.normal,
            premium=self.premium,
            total=self.total,
        )


class UpdateBuyTarget(CamelBaseModel):
    month: Months
    year: Annotated[str, StringConstraints(pattern=r"^\d{4}$")]
    normal: int
    premium: int
    total: int

    class config:
        orm_mode = True


class BuyTargetItem(CamelBaseModel):
    id: int
    user_name: str
    month: Months
    year: str
    normal: int
    premium: int
    total: int
    created_at: datetime
    created_by: str
    modified_at: datetime | None = None
    modified_by: str | None = None


class BuyTargetList(CamelBaseModel):
    total: int
    limit: int
    next: Optional[str]
    items: List[BuyTargetItem]


class EvaluationParameterRequest(CamelBaseModel):
    part_id: int
    subpart_id: int
    subpartstatus_id: int
    subpartsubstatus_id: int | None = None


class CreateBuyLeadPreprice(CamelBaseModel):
    pre_price: Decimal = Decimal("0.00")
    remarks: str = Field(..., min_length=1, max_length=500)

    class config:
        schema_extra = {"example": BUY_LEAD_PREPRICE}
        orm_mode = True

    def to_model(self) -> BuyModel.BuyLeadPreprice:
        return BuyModel.BuyLeadPreprice(
            pre_price=self.pre_price,
            remarks=self.remarks,
        )
