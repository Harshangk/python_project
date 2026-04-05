import csv
import io
from pathlib import Path
from typing import List
from uuid import UUID, uuid4

from api.schema_types import BuyStatus
from common.file_storage import AbstractFileStorage
from app.core.logging import logger
from model.buy.buy import BuyLead as BuyLeadModel, AllocateLeadsRequest
from repository.buy.buy_repository_interface import BuyRepositoryInterface
from schema.buy.buy import BuyLeadItem, LeadAddress, BuyLeadFollowupItem, BuyLeadFollowupDetail, BuyLeadAddress
from services.buy.csv_parser import BuyLeadCSVParser, ParsingError
from services.buy.buy_service_interface import BuyServiceInterface, ImportLeadResult
from app import constant


class BuyService(BuyServiceInterface):
    def __init__(
        self,
        buy_repository: BuyRepositoryInterface,
        file_storage: AbstractFileStorage,
    ) -> None:
        self.buy_repository = buy_repository
        self.file_storage = file_storage

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
        file_uuid: UUID | None = None,
    ) -> ImportLeadResult:
        if file_uuid is None:
            file_uuid = uuid4()
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

        parser = BuyLeadCSVParser(
            file=io.StringIO(decoded_content),
            buy_repository=self.buy_repository,
            source=source.strip(),
            broker_name=normalized_broker_name or None,
        )

        try:
            parsed_rows = await parser.parse()
        except ParsingError as ex:
            raise ValueError(str(ex)) from ex

        import_s3_key = self._upload_import_file(
            filename=filename or "import.csv",
            content=content,
            file_uuid=file_uuid,
        )
        await self._save_file_reference(
            s3_key=import_s3_key,
            file_type=constant.BUY_LEAD_IMPORT_FILE_TYPE,
            file_uuid=file_uuid,
        )
        headers = parser.headers
        invalid_rows: list[dict[str, str]] = []
        leads_to_create: list[BuyLeadModel] = []

        for result in parsed_rows:
            if result.error:
                invalid_row = {header: result.row.get(header, "") for header in headers}
                invalid_row["error"] = result.error
                invalid_rows.append(invalid_row)
                continue
            if result.parsed is not None:
                leads_to_create.append(result.parsed)

        if invalid_rows:
            error_csv_content = self._build_error_csv(
                headers=headers,
                invalid_rows=invalid_rows,
            )
            original_filename = (filename or "import.csv").strip() or "import.csv"
            filename_root = original_filename.rsplit(".", 1)[0]
            error_s3_key = self._upload_error_file(
                filename=f"{filename_root}_errors.csv",
                content=error_csv_content,
                file_uuid=file_uuid,
            )
            await self._save_file_reference(
                s3_key=error_s3_key,
                file_type=constant.BUY_LEAD_ERROR_FILE_TYPE,
                file_uuid=file_uuid,
            )
            created_count = 0
            for lead in leads_to_create:
                lead.file_uuid = file_uuid
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
            lead.file_uuid = file_uuid
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
        return csv_content.encode("utf-8")

    def _upload_import_file(self, filename: str, content: bytes, file_uuid: UUID) -> str:
        return self._upload_csv_file("import", filename, content, file_uuid)

    def _upload_error_file(self, filename: str, content: bytes, file_uuid: UUID) -> str:
        return self._upload_csv_file("error", filename, content, file_uuid)

    def _upload_csv_file(
        self,
        folder: str,
        filename: str,
        content: bytes,
        file_uuid: UUID,
        label: str | None = None,
    ) -> str:
        safe_filename = Path(filename).name or "import.csv"
        stem = Path(safe_filename).stem or "file"
        suffix = Path(safe_filename).suffix
        label_suffix = f"_{label}" if label else ""
        storage_filename = f"{folder}/{stem}{label_suffix}_{str(file_uuid)}{suffix}"
        return self.file_storage.upload_file(
            filename=storage_filename,
            file_obj=content,
        )

    async def _save_file_reference(self, s3_key: str, file_type: str, file_uuid: UUID) -> int:
        file_id = await self.buy_repository.create_lead_file(
            s3_key=s3_key,
            file_type=file_type,
            file_uuid=file_uuid,
        )
        logger.info(
            "Stored buy lead file metadata. file_id=%s file_type=%s file_uuid=%s s3_key=%s",
            file_id,
            file_type,
            file_uuid,
            s3_key,
        )
        return file_id
    
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
