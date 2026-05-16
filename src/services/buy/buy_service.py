import asyncio
import csv
import io
from io import BytesIO
from pathlib import Path
from typing import List
from uuid import UUID

from app import constant
from common.evaluation_pdf import build_buy_lead_evaluation_pdf
from common.file_storage import AbstractFileStorage
from common.payment_pdf import build_buy_lead_payment_pdf
from common.schema_types import BuyStage, BuyStatus, FileStatus
from model.buy.buy import AllocateLeadsRequest
from model.buy.buy import BuyLead as BuyLeadModel
from model.buy.buy import BuyLeadFollowup, BuyLeadPayment
from repository.buy.buy_repository_interface import BuyRepositoryInterface
from repository.common.common_repository_interface import CommonRepositoryInterface
from schema.buy.buy import (
    BuyLeadFollowupDetail,
    BuyLeadFollowupItem,
    BuyLeadImportItem,
    BuyLeadItem,
    LeadAddress,
    LeadFollowup,
)
from services.buy.buy_service_interface import BuyServiceInterface
from services.buy.buy_transform import transform


class BuyService(BuyServiceInterface):
    def __init__(
        self,
        buy_repository: BuyRepositoryInterface,
        file_storage: AbstractFileStorage,
        error_file_storage: AbstractFileStorage,
        evaluation_file_storage: AbstractFileStorage,
        common_repository: CommonRepositoryInterface,
    ) -> None:
        self.buy_repository = buy_repository
        self.file_storage = file_storage
        self.error_file_storage = error_file_storage
        self.evaluation_file_storage = evaluation_file_storage
        self.common_repository = common_repository

    async def create_lead(self, lead: BuyLeadModel, created_by: str) -> int:
        return await self.buy_repository.create_lead(lead, created_by=created_by)

    async def update_lead(
        self, lead_id: int, lead: BuyLeadModel, created_by: str
    ) -> int:
        return await self.buy_repository.update_lead(
            lead_id, lead, created_by=created_by
        )

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
        leads = []

        followup_fields = set(LeadFollowup.model_fields)

        for row in rows:
            # Extract followup data
            lead_followup_data = {
                k: row[k] for k in followup_fields if k in row and row[k] is not None
            }

            lead_followup = (
                LeadFollowup(**lead_followup_data) if lead_followup_data else None
            )

            # Remaining fields
            item_data = {k: v for k, v in row.items() if k not in followup_fields}

            item_data["lead_followup"] = lead_followup

            leads.append(BuyLeadItem(**item_data))

        return leads

    async def get_total_lead(
        self, search: str | None = None, buy_status: BuyStatus | None = None
    ) -> int:
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

        lead_address_data = {
            k: row[k]
            for k in LeadAddress.model_fields
            if k in row and row[k] is not None
        }
        lead_address = LeadAddress(**lead_address_data) if lead_address_data else None
        item_data = {k: v for k, v in row.items() if k not in lead_address_data}
        item_data["lead_address"] = lead_address
        return BuyLeadItem(**item_data)

    async def remove_lead(self, lead_id: int, created_by: str) -> bool:
        return await self.buy_repository.remove_lead(lead_id, created_by)

    async def allocate_leads(
        self, allocate: AllocateLeadsRequest, created_by: str
    ) -> int:
        return await self.buy_repository.allocate_leads(allocate, created_by=created_by)

    async def reallocate_leads(
        self, reallocate: AllocateLeadsRequest, created_by: str
    ) -> int:
        return await self.buy_repository.reallocate_leads(
            reallocate, created_by=created_by
        )

    async def reopen_leads(self, reopen: AllocateLeadsRequest, created_by: str) -> int:
        return await self.buy_repository.reopen_leads(reopen, created_by=created_by)

    async def create_lead_followup(
        self, lead_id: int, lead: BuyLeadFollowup, created_by: str
    ) -> int:
        return await self.buy_repository.create_lead_followup(
            lead_id=lead_id, lead=lead, created_by=created_by
        )

    async def get_followup_lead(
        self,
        cursor: int | None,
        limit: int,
        created_by: str,
        role_id: int,
        search: str | None = None,
        buy_stage: BuyStage | None = None,
    ) -> List[BuyLeadFollowupItem]:
        rows = await self.buy_repository.get_followup_lead(
            cursor, limit, created_by, role_id, search, buy_stage
        )
        leads = []

        followup_fields = set(LeadFollowup.model_fields)

        for row in rows:
            # Extract followup data
            lead_followup_data = {
                k: row[k] for k in followup_fields if k in row and row[k] is not None
            }

            lead_followup = (
                LeadFollowup(**lead_followup_data) if lead_followup_data else None
            )

            # Remaining fields
            item_data = {k: v for k, v in row.items() if k not in followup_fields}

            item_data["lead_followup"] = lead_followup

            leads.append(BuyLeadFollowupItem(**item_data))

        return leads

    async def get_total_followup_lead(
        self,
        created_by: str,
        role_id: int,
        search: str | None = None,
        buy_stage: BuyStage | None = None,
    ) -> int:
        return await self.buy_repository.get_total_followup_lead(
            created_by, role_id, search, buy_stage
        )

    async def get_followup_lead_export(
        self,
        created_by: str,
        role_id: int,
        search: str | None = None,
        buy_stage: BuyStage | None = None,
    ):
        async for row in self.buy_repository.get_followup_lead_export(
            created_by, role_id, search, buy_stage
        ):
            lead_followup_data = {
                k: row[k]
                for k in LeadFollowup.model_fields
                if k in row and row[k] is not None
            }
            lead_followup = (
                LeadFollowup(**lead_followup_data) if lead_followup_data else None
            )

            item_data = {k: v for k, v in row.items() if k not in lead_followup_data}

            item_data["lead_followup"] = lead_followup
            yield BuyLeadFollowupItem(**item_data)

    async def get_followup_lead_by_id(
        self,
        lead_id: int,
        created_by: str,
        role_id: int,
    ) -> BuyLeadFollowupDetail:
        row = await self.buy_repository.get_followup_lead_by_id(
            lead_id, created_by, role_id
        )
        if not row:
            return None
        # Extract address
        lead_address_data = {
            k: row[k]
            for k in LeadAddress.model_fields
            if k in row and row[k] is not None
        }
        lead_address = LeadAddress(**lead_address_data) if lead_address_data else None

        # Extract followup
        lead_followup_data = {
            k: row[k]
            for k in LeadFollowup.model_fields
            if k in row and row[k] is not None
        }
        lead_followup = (
            LeadFollowup(**lead_followup_data) if lead_followup_data else None
        )

        # Remaining fields
        item_data = {
            k: v
            for k, v in row.items()
            if k not in lead_address_data and k not in lead_followup_data
        }

        item_data["lead_address"] = lead_address
        item_data["lead_followup"] = lead_followup
        return BuyLeadFollowupDetail(**item_data)

    async def buy_lead_file_upload(
        self,
        filename: str,
        file_path: str | None = None,
        file_bytes: bytes | None = None,
        content_type: str | None = None,
    ) -> str:
        file_obj = io.BytesIO(file_bytes)
        file_obj.seek(0)

        s3_key = await asyncio.to_thread(
            self.file_storage.upload_file,
            filename=filename,
            file_obj=file_obj,
            content_type=content_type,
        )
        return s3_key

    async def create_lead_file_id(
        self,
        file_uuid: UUID,
        s3_key: str,
        status: FileStatus,
        created_by: str,
    ) -> int:
        return await self.buy_repository.create_lead_file_id(
            file_uuid=file_uuid,
            s3_key=s3_key,
            status=status,
            created_by=created_by,
        )

    async def process_file(
        self,
        file_uuid,
        s3_key: str,
        created_by: str,
        source: str,
        broker_name: str | None = None,
    ):
        try:
            reader = await self._get_csv_reader(s3_key)

            make_map, model_map, branch_map = await self._load_mappings()

            processed_records, error_records, error_rows = await self._process_rows(
                reader,
                file_uuid,
                source,
                broker_name,
                created_by,
                make_map,
                model_map,
                branch_map,
            )

            error_file_key = await self._upload_error_file(file_uuid, error_rows)

            await self._update_status(
                file_uuid,
                FileStatus.Complete.value,
                processed_records,
                error_records,
                error_file_key,
            )

        except Exception:
            await self._update_status(
                file_uuid,
                FileStatus.Failed.value,
                processed_records,
                error_records,
                error_file_key,
            )

    async def _get_csv_reader(self, s3_key: str):
        file_obj = io.BytesIO()

        await asyncio.to_thread(self.file_storage.download_file, s3_key, file_obj)

        file_obj.seek(0)

        text_stream = io.TextIOWrapper(file_obj, encoding="utf-8")

        return csv.DictReader(text_stream)

    async def _load_mappings(self):
        make_map = await self.common_repository.get_make_map()
        model_map = await self.common_repository.get_model_map()
        branch_map = await self.common_repository.get_branch_map()
        return make_map, model_map, branch_map

    async def _process_rows(
        self,
        reader,
        file_uuid,
        source,
        broker_name,
        created_by,
        make_map,
        model_map,
        branch_map,
    ):
        batch = []
        error_rows = []

        processed_records = 0
        error_records = 0

        batch_size = constant.BATCHSIZE

        for row in reader:
            try:
                transformed, error = transform(
                    row,
                    file_uuid,
                    created_by,
                    make_map,
                    model_map,
                    branch_map,
                    source,
                    broker_name,
                )

                if transformed:
                    batch.append(transformed)
                    processed_records += 1
                else:
                    error_records += 1
                    error_rows.append(self._build_error_row(row, error))

            except Exception as e:
                error_records += 1
                error_rows.append(self._build_error_row(row, str(e)))

            if len(batch) >= batch_size:
                await self.buy_repository.bulk_insert_lead(batch)
                batch.clear()
        if batch:
            await self.buy_repository.bulk_insert_lead(batch)

        return processed_records, error_records, error_rows

    def _build_error_row(self, row: dict, error: str) -> dict:
        error_row = dict(row)
        error_row["error"] = error
        return error_row

    async def _upload_error_file(self, file_uuid, error_rows):
        if not error_rows:
            return None

        output = io.StringIO()

        fieldnames = list(error_rows[0].keys())

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(error_rows)

        error_bytes = io.BytesIO(output.getvalue().encode("utf-8"))

        error_filename = f"{file_uuid}_error.csv"

        return await asyncio.to_thread(
            self.error_file_storage.upload_file,
            filename=error_filename,
            file_obj=error_bytes,
            content_type="text/csv",
        )

    async def _update_status(
        self,
        file_uuid,
        status,
        processed_records,
        error_records,
        error_file_key,
    ):
        await self.buy_repository.patch_file_status(
            file_uuid,
            status,
            processed_records,
            error_records,
            error_file_key,
        )

    async def get_import_lead(
        self,
        cursor: int | None,
        limit: int,
        created_by: str,
        role_id: int,
        search: str | None = None,
    ) -> List[BuyLeadImportItem]:
        rows = await self.buy_repository.get_import_lead(
            cursor, limit, created_by, role_id, search
        )
        leads = [BuyLeadImportItem(**row) for row in rows]
        return leads

    async def get_total_import_lead(
        self,
        created_by: str,
        role_id: int,
        search: str | None = None,
    ) -> int:
        return await self.buy_repository.get_total_import_lead(
            created_by, role_id, search
        )

    async def get_import_lead_export(
        self,
        created_by: str,
        role_id: int,
        search: str | None = None,
    ):
        async for row in self.buy_repository.get_import_lead_export(
            created_by, role_id, search
        ):
            yield BuyLeadImportItem(**row)

    async def get_import_lead_by_id(
        self,
        import_id: int,
        created_by: str,
        role_id: int,
    ) -> BuyLeadImportItem:
        row = await self.buy_repository.get_import_lead_by_id(
            import_id, created_by, role_id
        )
        if not row:
            return None
        return BuyLeadImportItem(**row)

    async def create_lead_payment(
        self, lead_payment: BuyLeadPayment, created_by: str
    ) -> int:
        return await self.buy_repository.create_lead_payment(
            lead_payment=lead_payment, created_by=created_by
        )

    async def get_lead_payment_pdf(
        self,
        lead_id: int,
        created_by: str,
        role_id: int,
    ) -> tuple[str, bytes] | None:
        payment = await self.buy_repository.get_lead_payment_pdf(
            lead_id=lead_id,
            created_by=created_by,
            role_id=role_id,
        )
        if not payment:
            return None

        filename = f"buy_lead_payment_{lead_id}.pdf"
        return filename, build_buy_lead_payment_pdf(payment)

    async def process_evaluation_photos(
        self,
        lead_id: int,
        processed_files: list[dict],
        created_by: str,
    ) -> None:
        try:

            async def upload_single_photo(
                item: dict,
            ) -> dict:
                photo_name = item["photo_name"]
                filename = item["filename"]
                file_bytes = item["file_bytes"]
                content_type = item["content_type"]
                extension = Path(filename).suffix.lower()

                s3_key = f"lead_{lead_id}/" f"{photo_name}{extension}"

                file_obj = BytesIO(file_bytes)

                uploaded_s3_key = await asyncio.to_thread(
                    self.evaluation_file_storage.upload_file,
                    filename=s3_key,
                    file_obj=file_obj,
                    content_type=content_type,
                )

                return {
                    "buylead_id": lead_id,
                    "photo_name": photo_name,
                    "s3_key": uploaded_s3_key,
                    "content_type": content_type,
                    "created_by": created_by,
                }

            # Concurrent uploads
            photo_records = await asyncio.gather(
                *[upload_single_photo(item) for item in processed_files]
            )

            # Bulk upsert
            await self.buy_repository.upsert_evaluation_photos(photo_records)
        except Exception:
            raise

    async def save_evaluation_parameters(
        self,
        lead_id: int,
        remarks: str,
        evaluation_parameters: list[dict],
        created_by: str,
    ) -> int:

        try:
            records = []
            for item in evaluation_parameters:
                records.append(
                    {
                        "buylead_id": lead_id,
                        "part_id": item["part_id"],
                        "subpart_id": item["subpart_id"],
                        "subpartstatus_id": item["subpartstatus_id"],
                        "subpartsubstatus_id": item.get("subpartsubstatus_id"),
                        "created_by": created_by,
                    }
                )
            return await self.buy_repository.save_evaluation_parameters(
                lead_id=lead_id,
                evaluation_parameters=records,
                remarks=remarks,
                created_by=created_by,
            )
        except Exception as ex:
            raise ex

    async def get_lead_evaluation_pdf(
        self,
        lead_id: int,
        created_by: str,
        role_id: int,
    ) -> tuple[str, bytes] | None:
        evaluation = await self.buy_repository.get_lead_evaluation_pdf(
            lead_id=lead_id,
            created_by=created_by,
            role_id=role_id,
        )
        if not evaluation:
            return None

        photos = evaluation.get("photos", [])

        async def load_photo(photo):
            image_bytes = await asyncio.to_thread(
                self.evaluation_file_storage.download_file, photo["s3_key"]
            )

            return {
                "photo_name": photo.get("photo_name"),
                "photo_type": photo.get("photo_type"),
                "image_bytes": image_bytes,
            }

        evaluation["photos"] = await asyncio.gather(*(load_photo(p) for p in photos))

        filename = f"buy_lead_evaluation_{lead_id}.pdf"
        return filename, build_buy_lead_evaluation_pdf(evaluation)
