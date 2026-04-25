import asyncio
import io
from typing import List

from botocore.exceptions import ClientError

from app import constant
from common.file_storage import AbstractFileStorage
from common.schema_types import Bucket
from repository.common.common_repository_interface import CommonRepositoryInterface
from schema.common.common import (
    BranchItem,
    BrokerItem,
    CityItem,
    LeadSourceItem,
    MakeItem,
    ModelItem,
    StateItem,
    YearItem,
)
from services.common.common_service_interface import CommonServiceInterface


class CommonService(CommonServiceInterface):
    def __init__(
        self,
        common_repository: CommonRepositoryInterface,
        file_storage: AbstractFileStorage,
        error_file_storage: AbstractFileStorage,
    ) -> None:
        self.common_repository = common_repository
        self.file_storage = file_storage
        self.error_file_storage = error_file_storage

    async def get_source(
        self,
        cursor: int | None,
        limit: int,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> List[LeadSourceItem]:
        rows = await self.common_repository.get_source(
            cursor, limit, search, sort_by, sort_order
        )
        source = [LeadSourceItem(**row) for row in rows]
        return source

    async def get_total_source(self, search: str | None = None) -> int:
        return await self.common_repository.get_total_source(search)

    async def validate_source(self, source: str | None = None) -> bool:
        return await self.common_repository.validate_source(source)

    async def get_make(
        self,
        cursor: int | None,
        limit: int,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> List[MakeItem]:
        rows = await self.common_repository.get_make(
            cursor, limit, search, sort_by, sort_order
        )
        make = [MakeItem(**row) for row in rows]
        return make

    async def get_total_make(self, search: str | None = None) -> int:
        return await self.common_repository.get_total_make(search)

    async def get_model(
        self,
        cursor: int | None,
        limit: int,
        make_id: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> List[ModelItem]:
        rows = await self.common_repository.get_model(
            make_id=make_id,
            cursor=cursor,
            limit=limit,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        model = [ModelItem(**row) for row in rows]
        return model

    async def get_total_model(
        self, make_id: int | None = None, search: str | None = None
    ) -> int:
        return await self.common_repository.get_total_model(
            make_id=make_id, search=search
        )

    async def get_branch(
        self,
        cursor: int | None,
        limit: int,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> List[BranchItem]:
        rows = await self.common_repository.get_branch(
            cursor, limit, search, sort_by, sort_order
        )
        branch = [BranchItem(**row) for row in rows]
        return branch

    async def get_total_branch(self, search: str | None = None) -> int:
        return await self.common_repository.get_total_branch(search)

    async def get_broker(
        self,
        cursor: int | None,
        limit: int,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> List[BrokerItem]:
        rows = await self.common_repository.get_broker(
            cursor, limit, search, sort_by, sort_order
        )
        broker = [BrokerItem(**row) for row in rows]
        return broker

    async def get_total_broker(self, search: str | None = None) -> int:
        return await self.common_repository.get_total_broker(search)

    async def validate_broker(self, broker: str | None = None) -> bool:
        return await self.common_repository.validate_broker(broker)

    async def get_year(
        self,
        cursor: int | None,
        limit: int,
        search: str | None = None,
    ) -> List[YearItem]:
        rows = await self.common_repository.get_year(cursor, limit, search)
        year = [YearItem(**row) for row in rows]
        return year

    async def get_total_year(self, search: str | None = None) -> int:
        return await self.common_repository.get_total_year(search)

    async def get_state(
        self,
        cursor: int | None,
        limit: int,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> List[StateItem]:
        rows = await self.common_repository.get_state(
            cursor, limit, search, sort_by, sort_order
        )
        state = [StateItem(**row) for row in rows]
        return state

    async def get_total_state(self, search: str | None = None) -> int:
        return await self.common_repository.get_total_state(search)

    async def get_city(
        self,
        cursor: int | None,
        limit: int,
        state_id: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> List[CityItem]:
        rows = await self.common_repository.get_city(
            state_id=state_id,
            cursor=cursor,
            limit=limit,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        city = [CityItem(**row) for row in rows]
        return city

    async def get_total_city(
        self, state_id: int | None = None, search: str | None = None
    ) -> int:
        return await self.common_repository.get_total_city(
            state_id=state_id, search=search
        )

    async def download_s3_file(
        self,
        s3_key: str,
        bucket: Bucket,
    ) -> int:
        try:
            file_obj = io.BytesIO()

            if bucket == Bucket.BuyFile.value:
                await asyncio.to_thread(
                    self.file_storage.download_file, s3_key, file_obj
                )
            else:
                await asyncio.to_thread(
                    self.error_file_storage.download_file, s3_key, file_obj
                )
            file_obj.seek(0)
            return file_obj, s3_key
        except ClientError:
            raise ValueError(constant.MISSINGFILES)
