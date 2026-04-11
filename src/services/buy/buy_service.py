import asyncio
import csv
import io
from typing import List
from uuid import UUID

from app import constant
from common.file_storage import AbstractFileStorage
from common.schema_types import BuyStatus, FileStatus
from model.buy.buy import AllocateLeadsRequest
from model.buy.buy import BuyLead as BuyLeadModel
from model.buy.buy import BuyLeadFollowup
from repository.buy.buy_repository_interface import BuyRepositoryInterface
from schema.buy.buy import (
    BuyLeadFollowupDetail,
    BuyLeadFollowupItem,
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
    ) -> None:
        self.buy_repository = buy_repository
        self.file_storage = file_storage

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
        leads = [BuyLeadItem(**row) for row in rows]
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
    ) -> List[BuyLeadFollowupItem]:
        rows = await self.buy_repository.get_followup_lead(
            cursor, limit, created_by, role_id, search
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
    ) -> int:
        return await self.buy_repository.get_total_followup_lead(
            created_by, role_id, search
        )

    async def get_followup_lead_export(
        self,
        created_by: str,
        role_id: int,
        search: str | None = None,
    ):
        async for row in self.buy_repository.get_followup_lead_export(
            created_by, role_id, search
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
        source: str,
        created_by: str,
    ):
        file_obj = io.BytesIO()
        await asyncio.to_thread(self.file_storage.download_file, s3_key, file_obj)
        file_obj.seek(0)

        text_stream = io.TextIOWrapper(file_obj, encoding="utf-8")

        reader = csv.DictReader(text_stream)

        batch = []
        BATCH_SIZE = constant.BATCHSIZE

        total = 0
        for row in reader:
            transformed = transform(row, file_uuid, source, created_by)

            if transformed:
                batch.append(transformed)

            if len(batch) >= BATCH_SIZE:
                await self.buy_repository.bulk_insert_lead(batch)
                total += len(batch)
                batch = []

        if batch:
            await self.buy_repository.bulk_insert_lead(batch)
            total += len(batch)

        await self.buy_repository.patch_file_status(
            file_uuid, FileStatus.Complete.value, total
        )
