from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional, Sequence
from api.schema_types import BuyStatus
from model.buy.buy import BuyLead as BuyLeadModel, AllocateLeadsRequest,BuyLeadFollowupDetail


class BuyRepositoryInterface(ABC):

    @abstractmethod
    async def create_lead(self, lead: BuyLeadModel, created_by: str) -> int:
        pass

    @abstractmethod
    async def update_lead(self, lead_id: int, lead: BuyLeadModel, created_by: str) -> int:
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
    ) -> Sequence[Mapping[str, Any]]:
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
    ) -> BuyLeadModel:
        pass

    @abstractmethod
    async def remove_lead(
        self,
        lead_id: int,
        created_by: str
    ) -> bool:
        pass


    @abstractmethod
    async def allocate_leads(self, allocate: AllocateLeadsRequest, created_by: str) -> int:
        pass

    @abstractmethod
    async def reallocate_leads(self, reallocate: AllocateLeadsRequest, created_by: str) -> int:
        pass

    @abstractmethod
    async def get_followup_lead(
        self,
        cursor: Optional[int],
        limit: int,
        created_by: str,
        role_id: int,
        search: str | None = None,
    ) -> Sequence[Mapping[str, Any]]:
        pass

    @abstractmethod
    async def get_total_followup_lead(
        self,
        created_by: str,
        role_id: int,
        search: str | None = None,
    ) -> int:
        pass

    @abstractmethod
    async def get_followup_lead_export(
        self,
        created_by: str,
        role_id: int,
        search: str | None = None,
    ):
        pass

    @abstractmethod
    async def get_followup_lead_by_id(
        self,
        lead_id: int,
        created_by: str,
        role_id: int,
    ) -> BuyLeadFollowupDetail:
        pass
