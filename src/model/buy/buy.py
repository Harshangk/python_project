from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic.dataclasses import dataclass

from common.schema_types import (
    BuyMode,
    BuyStatus,
    Category,
    Color,
    CommonFieldStatus,
    FileStatus,
    FuelType,
    InsuranceType,
    MemoPaid,
    Months,
    Transmission,
)


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
    category: Category
    customer_name: str
    owner_name: str
    payment_name: str
    make_id: int
    model_id: int
    fuel_type: FuelType
    mfg_month: Months
    mfg_year: str
    kms: int
    owner: str
    client_offer: int
    our_offer: int
    remarks: str
    status: BuyStatus | None = None
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
    mfg_month: Months
    mfg_year: str
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
    mfg_month: Months
    mfg_year: str
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
    mfg_month: Months
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


@dataclass
class BuyLeadVehicle:
    buylead_id: int
    registration_no: str
    transmission: Transmission
    cubic_capacity: int
    chassis_no: str
    engine_no: str
    push_button: CommonFieldStatus | None = None
    company_invoice: CommonFieldStatus | None = None
    noc: CommonFieldStatus | None = None
    reg_month: Months | None = None
    reg_year: str | None = None
    euro: str | None = None
    rc_book: CommonFieldStatus | None = None
    second_key: CommonFieldStatus | None = None
    hypo: CommonFieldStatus | None = None
    hypo_bank: str | None = None
    service_record: CommonFieldStatus | None = None
    puc: CommonFieldStatus | None = None
    memo: CommonFieldStatus | None = None
    memo_amount: Decimal = Decimal("0.00")
    memo_paid: MemoPaid | None = None
    mv_tax: Decimal = Decimal("0.00")
    rma: str | None = None
    taxi_private: str | None = None
    other_noc: str | None = None
    blacklist: str | None = None
    rto_status: str | None = None


@dataclass
class BuyLeadVehicleInsurance:
    buylead_id: int
    online_insurance: CommonFieldStatus | None = None
    insurance_type: InsuranceType | None = None
    cp_zd_company: str | None = None
    tp_company: str | None = None
    cp_zd_date: datetime | None = None
    tp_date: datetime | None = None
    idv: Decimal = Decimal("0.00")
    ncb: Decimal = Decimal("0.00")
    premium: Decimal = Decimal("0.00")


@dataclass
class BuyLeadPayment:
    buylead_id: int
    remarks: str
    created_by: str
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
    lead_vehicle: BuyLeadVehicle | None = None
    lead_vehicle_insurance: BuyLeadVehicleInsurance | None = None


@dataclass
class BuyLeadEvaluationParameter:
    buylead_id: int
    part_id: int
    subpart_id: int
    subpartstatus_id: int
    subpartsubstatus_id: int | None = None


@dataclass
class BuyLeadEvaluationPhoto:
    buylead_id: int
    photo_name: str
    s3_key: str
    content_type: str | None = None


@dataclass
class BuyLeadStockinDocument:
    buylead_id: int
    document_name: str
    s3_key: str
    content_type: str | None = None


@dataclass
class BuyLeadStockin:
    buylead_id: int
    remarks: str
    created_by: str
    lead_vehicle: BuyLeadVehicle | None = None
    lead_vehicle_insurance: BuyLeadVehicleInsurance | None = None
    documents: List[BuyLeadStockinDocument] | None = None


@dataclass
class BuyLeadTarget:
    user_name: str
    month: Months
    year: str
    normal: int
    premium: int
    total: int
    created_by: str | None = None


@dataclass
class BuyLeadEvaluation:
    buylead_id: int
    lead: UpdateLead
    created_by: str
    lead_vehicle: BuyLeadVehicle | None = None
    lead_vehicle_insurance: BuyLeadVehicleInsurance | None = None
    evaluation_parameters: List[BuyLeadEvaluationParameter] | None = None
    photos: List[BuyLeadEvaluationPhoto] | None = None


@dataclass
class BuyLeadPreprice:
    remarks: str
    pre_price: Decimal = Decimal("0.00")
    created_by: str | None = None
