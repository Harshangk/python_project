from typing import Optional

from pydantic.dataclasses import dataclass

from api.schema_types import BuyMode, Color, FuelType


@dataclass
class BuyLead:
    mobile: str
    alternate_mobile: Optional[str]
    source: str
    mode: BuyMode
    broker_name: str
    customer_name: str
    make_id: int
    model_id: int
    variant: str
    color: Color
    fuel_type: FuelType
    year: int
    kms: int
    owner: str
    client_offer: int
    our_offer: int
    telecaller: str
    executive: str
    remarks: str
    created_by: str | None = None
