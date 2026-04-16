import csv
import io
from datetime import datetime, timedelta
from enum import Enum
from typing import TypeVar

from fastapi import HTTPException, status
from pydantic import BaseModel as PydanticBaseModel

from app.constant import EXTENSION, FILELARGE, FILENAME, INVALIDCSV, MISSINGCOLUMNS
from app.core.config import settings


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


async def validate_file_extension(filename: str, allowed_extensions: set[str]):
    if not filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=FILENAME)

    ext = filename.split(".")[-1].lower()

    if ext not in allowed_extensions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=EXTENSION)


async def validate_file_size(file_bytes: bytes):
    size = len(file_bytes)
    if size > settings.max_file_size:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, FILELARGE)


async def validate_csv_headers(file_bytes: bytes, required_columns: set):
    file_obj = io.BytesIO(file_bytes)
    text_stream = io.TextIOWrapper(file_obj, encoding="utf-8")

    reader = csv.DictReader(text_stream)

    if not reader.fieldnames:
        raise ValueError(status.HTTP_400_BAD_REQUEST, INVALIDCSV)

    missing_columns = required_columns - set(reader.fieldnames)

    if missing_columns:
        raise ValueError(status.HTTP_400_BAD_REQUEST, MISSINGCOLUMNS)


def clean_str(value: str | None) -> str | None:
    if value and value.strip():
        return value.strip()
    return None


def to_int(value):
    try:
        if not value:
            return None
        value = str(value).replace(",", "")
        return int(float(value))
    except Exception:
        return None


def to_float(value):
    try:
        if not value:
            return None
        value = str(value).replace(",", "")
        return float(value)
    except Exception:
        return None


def generate_time_slots(start_hour=9, end_hour=20):
    slots = []

    current = datetime.strptime(f"{start_hour}:00", "%H:%M")
    end = datetime.strptime(f"{end_hour}:00", "%H:%M")

    while current < end:
        next_time = current + timedelta(hours=1)

        slot = f"{current.strftime('%I:%M %p')} to {next_time.strftime('%I:%M %p')}"
        slots.append(slot)

        current = next_time

    return slots


class BuyStatus(str, Enum):
    NotAllocated = "NotAllocated"
    Allocated = "Allocated"
    Lost = "Lost"
    DND = "DND"
    Appointment = "Appointment"


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
    PriceIssue = "Price Issue"
    DND = "DND"


STAGE_DISPOSITION_MAP = {
    BuyStage.Fresh: [BuyDisposition.Fresh],
    BuyStage.UnderFollowup: [BuyDisposition.CallLater, BuyDisposition.NotContactable],
    BuyStage.Appointment: [BuyDisposition.Appointment],
    BuyStage.Lost: [BuyDisposition.NotInterested, BuyDisposition.PriceIssue],
    BuyStage.DND: [BuyDisposition.DND],
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


class FileStatus(str, Enum):
    Pending = "Pending"
    Processing = "Processing"
    Complete = "Complete"
    Partial = "Partial"
    Failed = "Failed"


class Bucket(str, Enum):
    BuyFile = settings.s3_bucket_name
    BuyFileError = settings.error_s3_bucket_name
