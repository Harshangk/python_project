from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from api.schema_types import BuyStatus
from model.buy.buy import BuyLead as BuyLeadModel, AllocateLeadsRequest
from schema.buy.buy import BuyLeadItem, BuyLeadFollowupItem, BuyLeadFollowupDetail


@dataclass
class ImportLeadResult:
    created_count: int
    error_csv_content: bytes | None = None
    error_filename: str | None = None
    failed_count: int = 0


class BuyServiceInterface(ABC):

    @abstractmethod
    async def create_lead(self, lead: BuyLeadModel, created_by: str) -> int:
        pass

    @abstractmethod
    async def import_lead_content(
        self,
        content: bytes,
        filename: str | None,
        source: str,
        broker_name: str | None = None,
        created_by: str | None = None,
        file_uuid: UUID | None = None,
    ) -> ImportLeadResult:
        pass

    @abstractmethod
    async def update_lead(self, lead_id:int, lead: BuyLeadModel, created_by: str) -> int:
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
    ) -> List[BuyLeadFollowupItem]:
        pass

    @abstractmethod
    async def get_total_followup_lead(
        self,
        created_by: str,
        role_id: int,
        search: str | None = None
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
