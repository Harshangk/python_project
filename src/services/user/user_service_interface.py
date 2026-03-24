from abc import ABC, abstractmethod
from typing import List, Optional

from model.user.user import User as UserModel
from schema.user.user import UserItem


class UserServiceInterface(ABC):

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
    ) -> List[UserItem]:
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
        search: str | None = None,
        role_id: int | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ):
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> UserItem:
        pass

    @abstractmethod
    async def lock_user(self, user_id: int) -> bool:
        pass
