import csv
import io
import re
from typing import List

from fastapi import UploadFile

from api.schema_types import BuyMode, BuyStatus, FuelType
from model.buy.buy import BuyLead as BuyLeadModel, AllocateLeadsRequest
from repository.buy.buy_repository_interface import BuyRepositoryInterface
from schema.buy.buy import BuyLeadItem
from services.buy.buy_service_interface import BuyServiceInterface
from app import constant


class BuyService(BuyServiceInterface):
    def __init__(self, buy_repository: BuyRepositoryInterface) -> None:
        self.buy_repository = buy_repository

    async def create_lead(self, lead: BuyLeadModel, created_by: str) -> int:
        return await self.buy_repository.create_lead(lead, created_by=created_by)

    async def validate_lead_import(self, file: UploadFile) -> None:
        content = await file.read()
        await file.seek(0)

        if not content:
            raise ValueError("CSV file is empty.")

        try:
            decoded_content = content.decode("utf-8-sig")
        except UnicodeDecodeError as ex:
            raise ValueError("CSV file must be UTF-8 encoded.") from ex

        reader = csv.DictReader(io.StringIO(decoded_content))
        if not reader.fieldnames:
            raise ValueError("CSV header is missing.")

        headers = [header.strip() if header else "" for header in reader.fieldnames]
        missing_headers = sorted(constant.REQUIRED_IMPORT_FIELDS - set(headers))
        if missing_headers:
            raise ValueError(
                f"Missing required CSV columns: {', '.join(missing_headers)}."
            )

        if any(header == "" for header in headers):
            raise ValueError("CSV contains an empty header column.")

        valid_modes = {mode.value for mode in BuyMode}
        valid_fuel_types = {fuel_type.value for fuel_type in FuelType}

        has_rows = False
        for row_number, row in enumerate(reader, start=2):
            has_rows = True
            normalized_row = {
                (key.strip() if key else ""): (value.strip() if value else "")
                for key, value in row.items()
            }
            self._validate_import_row(
                row=normalized_row,
                row_number=row_number,
                valid_modes=valid_modes,
                valid_fuel_types=valid_fuel_types,
            )

        if not has_rows:
            raise ValueError("CSV file must contain at least one data row.")

    async def get_lead(
        self,
        cursor: int | None,
        limit: int,
        search: str | None = None,
        buy_status: BuyStatus | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> List[BuyLeadItem]:
        rows = await self.buy_repository.get_lead(
            cursor, limit, search, buy_status, sort_by, sort_order
        )
        leads = [BuyLeadItem(**row) for row in rows]
        return leads

    async def get_total_lead(self, search: str | None = None,buy_status: BuyStatus | None = None) -> int:
        return await self.buy_repository.get_total_lead(search, buy_status)

    async def get_lead_export(
        self,
        search: str | None = None,
        buy_status: BuyStatus | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ):
        async for row in self.buy_repository.get_lead_export(
            search, buy_status, sort_by, sort_order
        ):
            yield BuyLeadItem(**row)

    async def get_lead_by_id(
        self,
        lead_id: int,
    ) -> BuyLeadItem:
        row = await self.buy_repository.get_lead_by_id(lead_id)
        if not row:
            return None
        return BuyLeadItem(**row)
    
    async def remove_lead(self, lead_id: int, created_by: str) -> bool:
        return await self.buy_repository.remove_lead(lead_id, created_by)
    

    async def allocate_leads(self, allocate: AllocateLeadsRequest, created_by: str) -> int:
        return await self.buy_repository.allocate_leads(allocate, created_by=created_by)

    def _validate_import_row(
        self,
        row: dict[str, str],
        row_number: int,
        valid_modes: set[str],
        valid_fuel_types: set[str],
    ) -> None:
        for field in constant.REQUIRED_IMPORT_FIELDS:
            if not row.get(field):
                raise ValueError(f"Row {row_number}: '{field}' is required.")

        customer_name = row["customer_name"]
        if not (1 <= len(customer_name) <= 255):
            raise ValueError(
                f"Row {row_number}: 'customer_name' must be between 1 and 255 characters."
            )

        mobile = row["mobile"]
        if not constant.MOBILE_PATTERN.fullmatch(mobile):
            raise ValueError(
                f"Row {row_number}: 'mobile' must start with 0 or 9 and contain exactly 10 digits."
            )

        if row["mode"] not in valid_modes:
            raise ValueError(
                f"Row {row_number}: 'mode' must be one of {', '.join(sorted(valid_modes))}."
            )

        if row["fuel_type"] not in valid_fuel_types:
            raise ValueError(
                f"Row {row_number}: 'fuel_type' must be one of {', '.join(sorted(valid_fuel_types))}."
            )

        year = row["year"]
        if not constant.YEAR_PATTERN.fullmatch(year):
            raise ValueError(f"Row {row_number}: 'year' must be a 4-digit value.")

        try:
            kms = int(row["kms"])
        except ValueError as ex:
            raise ValueError(f"Row {row_number}: 'kms' must be an integer.") from ex

        if kms < 0:
            raise ValueError(f"Row {row_number}: 'kms' must be zero or greater.")

        owner = row["owner"]
        if len(owner) != 1:
            raise ValueError(f"Row {row_number}: 'owner' must be a single character.")
