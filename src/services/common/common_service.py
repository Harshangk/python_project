from typing import List

from repository.common.common_repository_interface import CommonRepositoryInterface
from schema.common.common import (
    LeadSourceItem,
    MakeItem,
    ModelItem,
    BranchItem,
    YearItem,
    BrokerItem,
)
from services.common.common_service_interface import CommonServiceInterface


class CommonService(CommonServiceInterface):
    def __init__(self, common_repository: CommonRepositoryInterface) -> None:
        self.common_repository = common_repository

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
            sort_by= sort_by, 
            sort_order=sort_order
        )
        model = [ModelItem(**row) for row in rows]
        return model

    async def get_total_model(self, make_id: int | None = None, search: str | None = None) -> int:
        return await self.common_repository.get_total_model(make_id=make_id,search=search)
    
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
    
    async def get_year(
        self,
        cursor: int | None,
        limit: int,
        search: str | None = None,
    ) -> List[YearItem]:
        rows = await self.common_repository.get_year(
            cursor, limit, search
        )
        year = [YearItem(**row) for row in rows]
        return year

    async def get_total_year(self, search: str | None = None) -> int:
        return await self.common_repository.get_total_year(search)
