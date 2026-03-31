from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional, Sequence

from model.buy.buy import BuyLead as BuyLeadModel


class BuyRepositoryInterface(ABC):

    @abstractmethod
    async def create_lead(self, lead: BuyLeadModel, created_by: str) -> int:
        pass

    @abstractmethod
    async def get_lead(
        self,
        cursor: Optional[int],
        limit: int,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> Sequence[Mapping[str, Any]]:
        pass

    @abstractmethod
    async def get_total_lead(self, search: str | None = None) -> int:
        pass

    @abstractmethod
    async def get_lead_export(
        self,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ):
        pass

    @abstractmethod
    async def get_lead_by_id(
        self,
        lead_id: int,
    ) -> BuyLeadModel:
        pass

    @abstractmethod
    async def remove_lead(
        self,
        lead_id: int,
        created_by: str
    ) -> bool:
        pass
