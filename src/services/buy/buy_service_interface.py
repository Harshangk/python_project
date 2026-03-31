from abc import ABC, abstractmethod
from typing import List, Optional
from api.schema_types import BuyStatus
from model.buy.buy import BuyLead as BuyLeadModel
from schema.buy.buy import BuyLeadItem


class BuyServiceInterface(ABC):

    @abstractmethod
    async def create_lead(self, lead: BuyLeadModel, created_by: str) -> int:
        pass

    @abstractmethod
    async def get_lead(
        self,
        cursor: Optional[int],
        limit: int,
        search: str | None = None,
        buy_status: BuyStatus | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> List[BuyLeadItem]:
        pass

    @abstractmethod
    async def get_total_lead(self, search: str | None = None, buy_status: BuyStatus | None = None) -> int:
        pass

    @abstractmethod
    async def get_lead_export(
        self,
        search: str | None = None,
        buy_status: BuyStatus | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ):
        pass

    @abstractmethod
    async def get_lead_by_id(
        self,
        lead_id: int,
    ) -> BuyLeadItem:
        pass

    @abstractmethod
    async def remove_lead(
        self,
        lead_id: int,
        created_by: str
    ) -> bool:
        pass
