from abc import ABC, abstractmethod
from typing import List, Optional

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


class CommonServiceInterface(ABC):

    @abstractmethod
    async def get_source(
        self,
        cursor: Optional[int],
        limit: int,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> List[LeadSourceItem]:
        pass

    @abstractmethod
    async def get_total_source(self, search: str | None = None) -> int:
        pass

    @abstractmethod
    async def get_make(
        self,
        cursor: Optional[int],
        limit: int,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> List[MakeItem]:
        pass

    @abstractmethod
    async def get_total_make(self, search: str | None = None) -> int:
        pass

    @abstractmethod
    async def get_model(
        self,
        cursor: Optional[int],
        limit: int,
        make_id: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> List[ModelItem]:
        pass

    @abstractmethod
    async def get_total_model(self, make_id: int, search: str | None = None) -> int:
        pass

    @abstractmethod
    async def get_branch(
        self,
        cursor: Optional[int],
        limit: int,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> List[BranchItem]:
        pass

    @abstractmethod
    async def get_total_branch(self, search: str | None = None) -> int:
        pass

    @abstractmethod
    async def get_broker(
        self,
        cursor: Optional[int],
        limit: int,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> List[BrokerItem]:
        pass

    @abstractmethod
    async def get_total_broker(self, search: str | None = None) -> int:
        pass

    @abstractmethod
    async def get_year(
        self,
        cursor: Optional[int],
        limit: int,
        search: str | None = None,
    ) -> List[YearItem]:
        pass

    @abstractmethod
    async def get_total_year(self, search: str | None = None) -> int:
        pass

    @abstractmethod
    async def get_state(
        self,
        cursor: Optional[int],
        limit: int,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> List[StateItem]:
        pass

    @abstractmethod
    async def get_total_state(self, search: str | None = None) -> int:
        pass

    @abstractmethod
    async def get_city(
        self,
        cursor: Optional[int],
        limit: int,
        state_id: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> List[CityItem]:
        pass

    @abstractmethod
    async def get_total_city(self, state_id: int, search: str | None = None) -> int:
        pass
