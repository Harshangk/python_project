import csv
import io
from typing import List

from api.schema_types import BuyMode, BuyStatus, FuelType
from app.core.logging import logger
from model.buy.buy import BuyLead as BuyLeadModel, AllocateLeadsRequest
from repository.buy.buy_repository_interface import BuyRepositoryInterface
from schema.buy.buy import BuyLeadItem, LeadAddress, BuyLeadFollowupItem, BuyLeadFollowupDetail, BuyLeadAddress
from services.buy.buy_service_interface import BuyServiceInterface, ImportLeadResult
from app import constant


class BuyService(BuyServiceInterface):
    def __init__(self, buy_repository: BuyRepositoryInterface) -> None:
        self.buy_repository = buy_repository

    async def create_lead(self, lead: BuyLeadModel, created_by: str) -> int:
        return await self.buy_repository.create_lead(lead, created_by=created_by)

    async def update_lead(self, lead_id: int, lead: BuyLeadModel, created_by: str) -> int:
        return await self.buy_repository.update_lead(lead_id, lead, created_by=created_by)
    
    async def import_lead_content(
        self,
        content: bytes,
        filename: str | None,
        source: str,
        broker_name: str | None = None,
        created_by: str | None = None,
    ) -> ImportLeadResult:
        valid_sources = await self.buy_repository.get_active_sources()
        normalized_source = source.strip().lower()
        normalized_broker_name = (broker_name or "").strip()

        if not normalized_source:
            raise ValueError("'source' is required.")
        if normalized_source not in valid_sources:
            raise ValueError(
                f"'source' must exist in mstsource. Allowed values: {', '.join(sorted(valid_sources))}."
            )
        if normalized_source == "broker" and not normalized_broker_name:
            raise ValueError("'broker_name' is required when 'source' is 'broker'.")
        if not created_by:
            raise ValueError("'created_by' is required.")

        if not content:
            raise ValueError("CSV file is empty.")

        try:
            decoded_content = content.decode("utf-8-sig")
        except UnicodeDecodeError as ex:
            raise ValueError("CSV file must be UTF-8 encoded.") from ex

        reader = csv.DictReader(io.StringIO(decoded_content))
        if not reader.fieldnames:
            raise ValueError("CSV header is missing.")

        headers = [header.strip().lower() if header else "" for header in reader.fieldnames]
        missing_headers = sorted(constant.REQUIRED_IMPORT_FIELDS - set(headers))
        if missing_headers:
            raise ValueError(
                f"Missing required CSV columns: {', '.join(missing_headers)}."
            )

        if any(header == "" for header in headers):
            raise ValueError("CSV contains an empty header column.")

        valid_modes = {mode.value.lower() for mode in BuyMode}
        valid_fuel_types = {fuel_type.value.lower() for fuel_type in FuelType}
        invalid_rows: list[dict[str, str]] = []
        leads_to_create: list[BuyLeadModel] = []

        has_rows = False
        for _, row in enumerate(reader, start=2):
            has_rows = True
            normalized_row = {
                (key.strip().lower() if key else ""): (value.strip() if value else "")
                for key, value in row.items()
            }
            row_errors, lead_model = await self._validate_import_row(
                row=normalized_row,
                valid_modes=valid_modes,
                valid_fuel_types=valid_fuel_types,
                source=source.strip(),
                broker_name=normalized_broker_name or None,
            )
            if row_errors:
                invalid_row = {
                    header: normalized_row.get(header, "")
                    for header in headers
                }
                invalid_row["error"] = " | ".join(row_errors)
                invalid_rows.append(invalid_row)
            elif lead_model is not None:
                leads_to_create.append(lead_model)

        if not has_rows:
            raise ValueError("CSV file must contain at least one data row.")

        if invalid_rows:
            error_csv_content = self._build_error_csv(
                headers=headers,
                invalid_rows=invalid_rows,
            )
            original_filename = (filename or "import.csv").strip() or "import.csv"
            filename_root = original_filename.rsplit(".", 1)[0]
            created_count = 0
            for lead in leads_to_create:
                await self.create_lead(lead, created_by=created_by)
                created_count += 1
            result = ImportLeadResult(
                created_count=created_count,
                error_csv_content=error_csv_content,
                error_filename=f"{filename_root}_errors.csv",
                failed_count=len(invalid_rows),
            )
            if result.created_count == 0:
                logger.info(
                    "No valid buy lead records found. failed_count=%s error_filename=%s",
                    result.failed_count,
                    result.error_filename,
                )
            else:
                logger.info(
                    "ImportLeadResult: created_count=%s failed_count=%s error_filename=%s",
                    result.created_count,
                    result.failed_count,
                    result.error_filename,
                )
            return result

        created_count = 0
        for lead in leads_to_create:
            await self.create_lead(lead, created_by=created_by)
            created_count += 1
        result = ImportLeadResult(created_count=created_count)
        if result.created_count == 0:
            logger.info("No valid buy lead records found.")
        else:
            logger.info(
                "Buy Lead records inserted succesfully=%s",
                result.created_count,
            )
        return result

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
        
        lead_address_data = {k: row[k] for k in LeadAddress.model_fields if k in row and row[k] is not None}
        lead_address = LeadAddress(**lead_address_data) if lead_address_data else None
        item_data = {k: v for k, v in row.items() if k not in lead_address_data}
        item_data["lead_address"] = lead_address
        return BuyLeadItem(**item_data)
    
    async def remove_lead(self, lead_id: int, created_by: str) -> bool:
        return await self.buy_repository.remove_lead(lead_id, created_by)
    

    async def allocate_leads(self, allocate: AllocateLeadsRequest, created_by: str) -> int:
        return await self.buy_repository.allocate_leads(allocate, created_by=created_by)

    async def _validate_import_row(
        self,
        row: dict[str, str],
        valid_modes: set[str],
        valid_fuel_types: set[str],
        source: str,
        broker_name: str | None,
    ) -> tuple[list[str], BuyLeadModel | None]:
        errors: list[str] = []
        def add_error(message: str) -> None:
            errors.append(f"{message}")

        for field in constant.REQUIRED_IMPORT_FIELDS:
            if not row.get(field):
                add_error(f"'{field}' is required.")

        if row.get("customer_name") and not (1 <= len(row["customer_name"]) <= 255):
            add_error("'customer_name' must be between 1 to 255 characters.")

        mobile = row.get("mobile", "")
        if mobile and not constant.MOBILE_PATTERN.fullmatch(mobile):
            add_error("'mobile' must start with 0 or 9 and contain exactly 10 digits.")

        mode = row.get("mode", "")
        if mode and mode.lower() not in valid_modes:
            add_error(f"'mode' must be one of {', '.join(sorted(valid_modes))}.")

        fuel_type = row.get("fuel_type", "")
        if fuel_type and fuel_type.lower() not in valid_fuel_types:
            add_error(f"'fuel_type' must be one of {', '.join(sorted(valid_fuel_types))}.")

        year = row.get("year", "")
        if year and not constant.YEAR_PATTERN.fullmatch(year):
            add_error("'year' must be a 4-digit value.")

        try:
            kms = int(row["kms"]) if row.get("kms") else None
        except ValueError:
            add_error("'kms' must be an integer.")
            kms = None

        if kms is not None and kms < 0:
            add_error("'kms' must be zero or greater.")

        try:
            int(row["our_offer"]) if row.get("our_offer") else None
        except ValueError:
            add_error("'our_offer' must be an integer.")

        owner = row.get("owner", "")
        if owner and len(owner) != 1:
            add_error("'owner' must be a single character.")

        make_id = None
        model_id = None
        if row.get("make"):
            make_id = await self.buy_repository.get_make_id_by_name(row["make"])
            if make_id is None:
                add_error(f"'make' '{row['make']}' does not exist.")

        if make_id is not None and row.get("model"):
            model_id = await self.buy_repository.get_model_id_by_name(
                make_id, row["model"]
            )
            if model_id is None:
                add_error(
                    f"'model' '{row['model']}' does not exist for make '{row['make']}'."
                )

        if errors:
            return errors, None

        lead_model = BuyLeadModel(
            branch=row["branch"],
            mobile=row["mobile"],
            alternate_mobile=None,
            source=source,
            mode=self._get_buy_mode(mode),
            broker_name=broker_name,
            customer_name=row["customer_name"],
            make_id=make_id,
            model_id=model_id,
            variant=None,
            color=None,
            fuel_type=self._get_fuel_type(fuel_type),
            year=int(row["year"]),
            kms=int(row["kms"]),
            owner=row["owner"],
            client_offer=0,
            our_offer=int(row["our_offer"]),
            remarks="Imported from CSV",
            telecaller=None,
            executive=None,
            lead_address=None,
        )
        return [], lead_model

    def _get_buy_mode(self, mode: str) -> BuyMode:
        normalized_mode = mode.strip().lower()
        for buy_mode in BuyMode:
            if buy_mode.value.lower() == normalized_mode:
                return buy_mode
        raise ValueError(f"Unsupported mode: {mode}")

    def _get_fuel_type(self, fuel_type: str) -> FuelType:
        normalized_fuel_type = fuel_type.strip().lower()
        for item in FuelType:
            if item.value.lower() == normalized_fuel_type:
                return item
        raise ValueError(f"Unsupported fuel type: {fuel_type}")

    def _build_error_csv(
        self,
        headers: list[str],
        invalid_rows: list[dict[str, str]],
    ) -> bytes:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[*headers, "error"])
        writer.writeheader()
        writer.writerows(invalid_rows)
        csv_content = output.getvalue()
        logger.info("Generated error CSV:\n%s", csv_content)
        return csv_content.encode("utf-8")
    
    async def reallocate_leads(self, reallocate: AllocateLeadsRequest, created_by: str) -> int:
        return await self.buy_repository.reallocate_leads(reallocate, created_by=created_by)
    

    async def get_followup_lead(
        self,
        cursor: int | None,
        limit: int,
        created_by: str,
        role_id: int,
        search: str | None = None,
    ) -> List[BuyLeadFollowupItem]:
        rows = await self.buy_repository.get_followup_lead(
            cursor, limit,created_by, role_id ,search
        )
        leads = [BuyLeadFollowupItem(**row) for row in rows]
        return leads

    async def get_total_followup_lead(
        self,
        created_by: str,
        role_id: int,
        search: str | None = None,
    ) -> int:
        return await self.buy_repository.get_total_followup_lead(created_by, role_id ,search)

    async def get_followup_lead_export(
        self,
        created_by: str,
        role_id: int,
        search: str | None = None,
    ):
        async for row in self.buy_repository.get_followup_lead_export(
            created_by, role_id ,search
        ):
            yield BuyLeadFollowupItem(**row)

    async def get_followup_lead_by_id(
        self,
        lead_id: int,
        created_by: str,
        role_id: int,
    ) -> BuyLeadFollowupDetail:
        row = await self.buy_repository.get_followup_lead_by_id(lead_id, created_by, role_id)
        if not row:
            return None
        lead_address_data = {k: row[k] for k in BuyLeadAddress.model_fields if k in row and row[k] is not None}
        lead_address = BuyLeadAddress(**lead_address_data) if lead_address_data else None
        item_data = {k: v for k, v in row.items() if k not in lead_address_data}
        item_data["lead_address"] = lead_address
        return BuyLeadFollowupDetail(**item_data)
