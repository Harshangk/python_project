from typing import List

from model.buy.buy import BuyLead as BuyLeadModel, AllocateLeadsRequest
from repository.buy.buy_repository_interface import BuyRepositoryInterface
from schema.buy.buy import BuyLeadItem, LeadAddress, BuyLeadFollowupItem, BuyLeadFollowupDetail, BuyLeadAddress
from services.buy.buy_service_interface import BuyServiceInterface
from api.schema_types import BuyStatus

class BuyService(BuyServiceInterface):
    def __init__(self, buy_repository: BuyRepositoryInterface) -> None:
        self.buy_repository = buy_repository

    async def create_lead(self, lead: BuyLeadModel, created_by: str) -> int:
        return await self.buy_repository.create_lead(lead, created_by=created_by)
    
    async def update_lead(self, lead_id: int, lead: BuyLeadModel, created_by: str) -> int:
        return await self.buy_repository.update_lead(lead_id, lead, created_by=created_by)

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
