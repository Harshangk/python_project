from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional, Sequence



class CommonRepositoryInterface(ABC):

    @abstractmethod
    async def get_source(
        self,
        cursor: Optional[int],
        limit: int,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> Sequence[Mapping[str, Any]]:
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
    ) -> Sequence[Mapping[str, Any]]:
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
    ) -> Sequence[Mapping[str, Any]]:
        pass

    @abstractmethod
    async def get_total_model(self, make_id: int | None = None, search: str | None = None) -> int:
        pass

    @abstractmethod
    async def get_branch(
        self,
        cursor: Optional[int],
        limit: int,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> Sequence[Mapping[str, Any]]:
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
    ) -> Sequence[Mapping[str, Any]]:
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
    ) -> Sequence[Mapping[str, Any]]:
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
    ) -> Sequence[Mapping[str, Any]]:
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
    ) -> Sequence[Mapping[str, Any]]:
        pass

    @abstractmethod
    async def get_total_city(self, state_id: int | None = None, search: str | None = None) -> int:
        pass
