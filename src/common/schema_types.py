import csv
import io
import json
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path as FilePath
from typing import TypeVar

from fastapi import HTTPException, Path, UploadFile, status
from pydantic import BaseModel as PydanticBaseModel

from app.constant import (
    COUNTMISMATCH,
    DUPLICATE,
    EMPTYFILE,
    EXTENSION,
    FILELARGE,
    FILENAME,
    IMAGECONTENTTYPE,
    IMAGEEXTENSION,
    INVALID,
    INVALIDCSV,
    INVALIDPAYLOAD,
    MISSINGCOLUMNS,
    MOBILEERROR,
    PDFCONTENTTYPE,
    PDFEXTENSION,
)
from app.core.config import settings
from app.core.logging import logger


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


async def _validate_image(file: UploadFile, file_bytes: bytes):

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID,
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in settings.allowed_image_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=IMAGEEXTENSION
        )

    if file.content_type not in settings.allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=IMAGECONTENTTYPE
        )

    if len(file_bytes) > settings.max_image_size:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, FILELARGE)


async def _validate_document(file: UploadFile, file_bytes: bytes):

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID,
        )

    extension = FilePath(file.filename).suffix.lower()

    if extension not in settings.allowed_pdf_extension:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=PDFEXTENSION
        )

    if file.content_type not in settings.allowed_pdf_content_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=PDFCONTENTTYPE
        )

    if len(file_bytes) > settings.max_pdf_size:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, FILELARGE)


async def validate_stockin_documents(
    documents: str,
    files: list[UploadFile],
) -> list[dict]:
    try:
        document_mappings = json.loads(documents)
    except json.JSONDecodeError:
        logger.info("Invalid stockin documents payload")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALIDPAYLOAD,
        )

    if len(document_mappings) != len(files):
        logger.info(
            f"Stockin documents count mismatch: "
            f"{len(document_mappings)} != {len(files)}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=COUNTMISMATCH,
        )

    processed_documents = []
    used_document_names = set()

    for item in document_mappings:
        if "document_name" not in item or "index" not in item:
            logger.info(f"Invalid stockin mapping payload: {item}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=INVALIDPAYLOAD,
            )

        document_name = item["document_name"]
        try:
            index = int(item["index"])
        except (TypeError, ValueError):
            logger.info(f"Invalid index: {item}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=INVALID,
            )

        if index < 0 or index >= len(files):
            logger.info(f"Index out of range: {index}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=INVALID,
            )

        if document_name not in StockinDocuments._value2member_map_:
            logger.info(f"Invalid stockin document name: {document_name}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=INVALID,
            )

        if document_name in used_document_names:
            logger.info(f"Duplicate stockin document name: {document_name}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=DUPLICATE,
            )

        used_document_names.add(document_name)

        file = files[index]
        filename = file.filename.strip()
        file_bytes = await file.read()

        if not file_bytes:
            logger.info(f"Empty file uploaded: {filename}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=EMPTYFILE,
            )

        await _validate_document(file, file_bytes)

        processed_documents.append(
            {
                "document_name": document_name,
                "filename": filename,
                "file_bytes": file_bytes,
                "content_type": file.content_type,
            }
        )

    return processed_documents


async def validate_photos(
    photos: str,
    files: list[UploadFile],
) -> list[dict]:

    # Validate JSON
    try:
        photo_mappings = json.loads(photos)

    except json.JSONDecodeError:

        logger.info("Invalid photos payload")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALIDPAYLOAD,
        )

    # Count validation
    if len(photo_mappings) != len(files):

        logger.info(f"Files count mismatch: " f"{len(photo_mappings)} != {len(files)}")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=COUNTMISMATCH,
        )

    processed_files = []

    used_photo_names = set()

    for item in photo_mappings:

        # Validate payload structure
        if "photo_name" not in item or "index" not in item:

            logger.info(f"Invalid mapping payload: {item}")

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=INVALIDPAYLOAD,
            )

        photo_name = item["photo_name"]

        # Validate index
        try:
            index = int(item["index"])

        except (TypeError, ValueError):

            logger.info(f"Invalid index: {item}")

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=INVALID,
            )

        # Validate index range
        if index < 0 or index >= len(files):

            logger.info(f"Index out of range: {index}")

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=INVALID,
            )

        # Validate enum
        if photo_name not in Photos._value2member_map_:

            logger.info(f"Invalid photo name: {photo_name}")

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=INVALID,
            )

        # Duplicate validation
        if photo_name in used_photo_names:

            logger.info(f"Duplicate photo name: {photo_name}")

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=DUPLICATE,
            )

        used_photo_names.add(photo_name)

        file = files[index]

        filename = file.filename.strip()

        # Read file
        file_bytes = await file.read()

        # Empty validation
        if not file_bytes:

            logger.info(f"Empty file uploaded: {filename}")

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=EMPTYFILE,
            )

        # Validate image
        await _validate_image(file, file_bytes)

        processed_files.append(
            {
                "photo_name": photo_name,
                "filename": filename,
                "file_bytes": file_bytes,
                "content_type": file.content_type,
            }
        )

    return processed_files


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


def validate_mobile(v: str) -> str:
    if not (10 <= len(v) <= 15):
        raise ValueError(MOBILEERROR)
    if not v.isdigit():
        raise ValueError(MOBILEERROR)
    return v


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
    UnderFollowup = "UnderFollowup"
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


class CommonFieldStatus(str, Enum):
    Yes = "Yes"
    No = "No"
    NA = "NA"


class BuyMode(str, Enum):
    Branch = "Branch"
    Home = "Home"
    NotInspected = "NotInspected"


class Transmission(str, Enum):
    Auto = "Auto"
    Manual = "Manual"
    DCT = "DCT"
    AMT = "AMT"
    IMT = "IMT"
    CVT = "CVT"
    IVT = "IVT"
    DSG = "DSG"
    SMT = "SMT"
    MMT = "MMT"
    ECVT = "ECVT"


class InsuranceType(str, Enum):
    Nil = "Nil"
    CP = "CP"
    TP = "TP"
    ZD = "ZD"
    CPTP = "CPTP"
    ZDTP = "ZDTP"


class MemoPaid(str, Enum):
    US = "US"
    Customer = "Customer"


class Category(str, Enum):
    Individual = "Individual"
    Corporate = "Corporate"


class Months(str, Enum):
    January = "January"
    February = "February"
    March = "March"
    April = "April"
    May = "May"
    June = "June"
    July = "July"
    August = "August"
    September = "September"
    October = "October"
    November = "November"
    December = "December"


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


class Photos(str, Enum):
    Front = "Front"
    LHSideFront = "LHSideFront"
    RHSideFront = "RHSideFront"
    BackSide = "BackSide"
    RearSideDashboard = "RearSideDashboard"
    Engine = "Engine"
    RHSFrontTyre = "RHSFrontTyre"
    RHSRearTyre = "RHSRearTyre"
    LHSFrontTyre = "LHSFrontTyre"
    LHSRearTyre = "LHSRearTyre"
    Interior = "Interior"
    Interior_1 = "Interior_1"
    Interior_2 = "Interior_2"
    Interior_3 = "Interior_3"
    Other_1 = "Other_1"
    Other_2 = "Other_2"
    Other_3 = "Other_3"


class StockinDocuments(str, Enum):
    RC = "RC"
    Insurance = "Insurance"
    IDProof = "IDProof"
    Token = "Token"
    SecondKey = "2ndKey"
    Agreement = "Agreement"
    History = "History"
