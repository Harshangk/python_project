from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional, Sequence
from uuid import UUID

from common.schema_types import BuyStage, BuyStatus, FileStatus
from model.buy.buy import AllocateLeadsRequest
from model.buy.buy import BuyLead as BuyLeadModel
from model.buy.buy import (
    BuyLeadFile,
    BuyLeadFollowup,
    BuyLeadFollowupDetail,
    BuyLeadPayment,
    BuyLeadTarget,
    ProvideBuyLeadPreprice,
)


class BuyRepositoryInterface(ABC):

    @abstractmethod
    async def get_existing_duplicates(self, keys: list[tuple]):
        pass

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
        created_by: str,
        role_id: int,
        search: str | None = None,
        buy_status: BuyStatus | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> Sequence[Mapping[str, Any]]:
        pass

    @abstractmethod
    async def get_total_lead(
        self,
        created_by: str,
        role_id: int,
        search: str | None = None,
        buy_status: BuyStatus | None = None,
    ) -> int:
        pass

    @abstractmethod
    async def get_lead_export(
        self,
        created_by: str,
        role_id: int,
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
        created_by: str,
        role_id: int,
    ) -> BuyLeadModel:
        pass

    @abstractmethod
    async def remove_lead(self, lead_id: int, created_by: str, role_id: int) -> bool:
        pass

    @abstractmethod
    async def allocate_leads(
        self, allocate: AllocateLeadsRequest, created_by: str, role_id: int
    ) -> int:
        pass

    @abstractmethod
    async def reallocate_leads(
        self, reallocate: AllocateLeadsRequest, created_by: str, role_id: int
    ) -> int:
        pass

    @abstractmethod
    async def reopen_leads(
        self, reopen: AllocateLeadsRequest, created_by: str, role_id: int
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
        buy_stage: BuyStage | None = None,
    ) -> Sequence[Mapping[str, Any]]:
        pass

    @abstractmethod
    async def get_followup_lead_status_count(
        self,
        created_by: str,
        role_id: int,
    ) -> Sequence[Mapping[str, Any]]:
        pass

    @abstractmethod
    async def get_total_followup_lead(
        self,
        created_by: str,
        role_id: int,
        search: str | None = None,
        buy_stage: BuyStage | None = None,
    ) -> int:
        pass

    @abstractmethod
    async def get_followup_lead_export(
        self,
        created_by: str,
        role_id: int,
        search: str | None = None,
        buy_stage: BuyStage | None = None,
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
    async def create_lead_file_id(
        self,
        file_uuid: UUID,
        s3_key: str,
        status: FileStatus,
        created_by: str,
    ) -> int:
        pass

    @abstractmethod
    async def patch_file_status(
        self,
        file_uuid: UUID,
        status: FileStatus,
        processed_records: int,
        error_records: int,
        error_file_key: str | None = None,
    ) -> int:
        pass

    @abstractmethod
    async def bulk_insert_lead(self, data):
        pass

    @abstractmethod
    async def get_import_lead(
        self,
        cursor: Optional[int],
        limit: int,
        created_by: str,
        role_id: int,
        search: str | None = None,
    ) -> Sequence[Mapping[str, Any]]:
        pass

    @abstractmethod
    async def get_total_import_lead(
        self, created_by: str, role_id: int, search: str | None = None
    ) -> int:
        pass

    @abstractmethod
    async def get_import_lead_export(
        self,
        created_by: str,
        role_id: int,
        search: str | None = None,
    ):
        pass

    @abstractmethod
    async def get_import_lead_by_id(
        self,
        import_id: UUID,
        created_by: str,
        role_id: int,
    ) -> BuyLeadFile:
        pass

    @abstractmethod
    async def create_lead_payment(
        self, lead_payment: BuyLeadPayment, created_by: str
    ) -> int:
        pass

    @abstractmethod
    async def get_lead_payment_pdf(
        self,
        lead_id: int,
        created_by: str,
        role_id: int,
    ) -> Mapping[str, Any] | None:
        pass

    @abstractmethod
    async def upsert_evaluation_photos(
        self,
        evaluation_photos: list[dict],
    ) -> None:
        pass

    @abstractmethod
    async def upsert_stockin_documents(
        self,
        stockin_documents: list[dict],
    ) -> int:
        pass

    @abstractmethod
    async def save_stockin(
        self,
        lead_id: int,
        remarks: str,
        created_by: str,
    ) -> int:
        pass

    @abstractmethod
    async def save_evaluation_parameters(
        self,
        lead_id: int,
        evaluation_parameters: list[dict],
        remarks: str,
        created_by: str,
    ) -> int:
        pass

    @abstractmethod
    async def get_lead_evaluation_pdf(
        self,
        lead_id: int,
        created_by: str,
        role_id: int,
    ) -> Mapping[str, Any] | None:
        pass

    @abstractmethod
    async def create_buy_target(
        self, buy_target: BuyLeadTarget, created_by: str
    ) -> int:
        pass

    @abstractmethod
    async def get_buy_target(
        self,
        cursor: Optional[int],
        limit: int,
        created_by: str,
        role_id: int,
        search: str | None = None,
    ) -> Sequence[Mapping[str, Any]]:
        pass

    @abstractmethod
    async def get_total_buy_target(
        self,
        created_by: str,
        role_id: int,
        search: str | None = None,
    ) -> int:
        pass

    @abstractmethod
    async def get_buy_target_export(
        self,
        created_by: str,
        role_id: int,
        search: str | None = None,
    ):
        pass

    @abstractmethod
    async def get_buy_target_by_id(
        self,
        target_id: int,
        created_by: str,
        role_id: int,
    ) -> BuyLeadTarget:
        pass

    @abstractmethod
    async def update_buy_target(
        self, target_id: int, target: BuyLeadTarget, created_by: str
    ) -> int:
        pass

    @abstractmethod
    async def remove_buy_target(
        self, target_id: int, created_by: str, role_id: int
    ) -> bool:
        pass

    @abstractmethod
    async def sent_lead_preprice(self, lead_id: int, created_by: str) -> int:
        pass

    @abstractmethod
    async def provide_lead_preprice(
        self, lead_id: int, lead_preprice: ProvideBuyLeadPreprice, created_by: str
    ) -> int:
        pass
