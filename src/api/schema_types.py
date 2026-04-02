from enum import Enum
from typing import TypeVar

from pydantic import BaseModel as PydanticBaseModel


def to_camel(s: str) -> str:
    first, *others = s.split("_")
    return "".join([first.lower(), *map(str.title, others)])


class CamelBaseModel(PydanticBaseModel):
    class Config:
        alias_generator = to_camel
        validate_by_name = True


def to_human_readable(s: str) -> str:
    return " ".join(map(str.title, s.split("_")))


class HumanReadableBaseModel(PydanticBaseModel):
    class Config:
        alias_generator = to_human_readable
        validate_by_name = True


T = TypeVar("T")


class BuyStatus(str, Enum):
    NotAllocated = "NotAllocated"
    Allocated = "Allocated"
    Lost = "Lost"


class BuyStage(str, Enum):
    Fresh = "Fresh"
    UnderFollowup = "Under Followup"
    Appointment = "Appointment"
    Lost = "Lost"
    DND = "DND"


class BuyDisposition(str, Enum):
    Fresh = "Fresh"
    CallLater = "Call Later"
    NotContactable = "Not Contactable"
    Appointment = "Appointment"
    NotInterested = "Not Interested"
    PriceIssue="Price Issue"
    DND = "DND"

STAGE_DISPOSITION_MAP = {
    BuyStage.Fresh: [
        BuyDisposition.Fresh
    ],
    BuyStage.UnderFollowup: [
        BuyDisposition.CallLater,
        BuyDisposition.NotContactable
    ],
    BuyStage.Appointment: [
        BuyDisposition.Appointment
    ],
    BuyStage.Lost: [
        BuyDisposition.NotInterested,
        BuyDisposition.PriceIssue
    ], 
    BuyStage.DND: [
        BuyDisposition.DND
    ],
}

class BuyMode(str, Enum):
    Branch = "Branch"
    Home = "Home"
    NotInspected = "NotInspected"


class Color(str, Enum):
    Black = "Black"
    White = "White"
    Yellow = "Yellow"


class FuelType(str, Enum):
    Petrol = "Petrol"
    Disel = "Disel"
    Hybrid = "Hybrid"


class Owner(str, Enum):
    NotRegistered = "0"
    First = "1"
    Second = "2"
    Third = "3"
    Fourth = "4"
    Fifth = "5"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"
