from typing import List

from model.buy.buy import BuyLead as BuyLeadModel
from repository.buy.buy_repository_interface import BuyRepositoryInterface
from schema.buy.buy import BuyLeadItem
from services.buy.buy_service_interface import BuyServiceInterface


class BuyService(BuyServiceInterface):
    def __init__(self, buy_repository: BuyRepositoryInterface) -> None:
        self.buy_repository = buy_repository

    async def create_lead(self, lead: BuyLeadModel, created_by: str) -> int:
        return await self.buy_repository.create_lead(lead, created_by=created_by)

    async def get_lead(
        self,
        cursor: int | None,
        limit: int,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> List[BuyLeadItem]:
        rows = await self.buy_repository.get_lead(
            cursor, limit, search, sort_by, sort_order
        )
        leads = [BuyLeadItem(**row) for row in rows]
        return leads

    async def get_total_lead(self, search: str | None = None) -> int:
        return await self.buy_repository.get_total_lead(search)

    async def get_lead_export(
        self,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ):
        async for row in self.buy_repository.get_lead_export(
            search, sort_by, sort_order
        ):
            yield BuyLeadItem(**row)
