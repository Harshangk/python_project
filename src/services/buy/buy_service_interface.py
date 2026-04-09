from abc import ABC, abstractmethod
from typing import IO, List, Optional
from uuid import UUID

from common.schema_types import BuyStatus, FileStatus
from model.buy.buy import AllocateLeadsRequest
from model.buy.buy import BuyLead as BuyLeadModel
from model.buy.buy import BuyLeadFollowup
from schema.buy.buy import (BuyLeadFollowupDetail, BuyLeadFollowupItem,
                            BuyLeadItem)


class BuyServiceInterface(ABC):

    @abstractmethod
    async def create_lead(self, lead: BuyLeadModel, created_by: str) -> int:
        pass

    @abstractmethod
    async def update_lead(
        self, lead_id: int, lead: BuyLeadModel, created_by: str
    ) -> int:
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
    async def get_total_lead(
        self, search: str | None = None, buy_status: BuyStatus | None = None
    ) -> int:
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
    async def remove_lead(self, lead_id: int, created_by: str) -> bool:
        pass

    @abstractmethod
    async def allocate_leads(
        self, allocate: AllocateLeadsRequest, created_by: str
    ) -> int:
        pass

    @abstractmethod
    async def reallocate_leads(
        self, reallocate: AllocateLeadsRequest, created_by: str
    ) -> int:
        pass

    @abstractmethod
    async def create_lead_followup(
        self, lead_id: int, lead: BuyLeadFollowup, created_by: str
    ) -> int:
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
        self, created_by: str, role_id: int, search: str | None = None
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

    @abstractmethod
    async def buy_lead_file_upload(
        self,
        filename: str,
        file_path: str | None = None,
        file_obj: IO[bytes] | None = None,
        content_type: str | None = None,
    ) -> int:
        pass

    @abstractmethod
    async def create_lead_file_id(
        self, file_uuid: UUID, s3_key: str, status: FileStatus, created_by: str
    ) -> int:
        pass

    @abstractmethod
    async def process_file(
        self,
        file_uuid: UUID,
    ) -> int:
        pass
