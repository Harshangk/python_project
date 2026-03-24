from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional, Sequence

from model.user.user import User as UserModel


class UserRepositoryInterface(ABC):

    @abstractmethod
    async def create_user(self, user: UserModel, created_by: str) -> int:
        pass

    @abstractmethod
    async def get_user(
        self,
        cursor: Optional[int],
        limit: int,
        role_id: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> Sequence[Mapping[str, Any]]:
        pass

    @abstractmethod
    async def get_total_user(
        self,
        role_id: int | None = None,
        search: str | None = None
    ) -> int:
        pass

    @abstractmethod
    async def get_user_export(
        self,
        role_id: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ):
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: int):
        pass

    @abstractmethod
    async def lock_user(self, user_id: int) -> bool:
        pass
