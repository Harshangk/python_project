from typing import List

from model.user.user import User as UserModel
from repository.user.user_repository_interface import UserRepositoryInterface
from schema.user.user import UserItem
from services.user.user_service_interface import UserServiceInterface


class UserService(UserServiceInterface):
    def __init__(self, user_repository: UserRepositoryInterface) -> None:
        self.user_repository = user_repository

    async def create_user(self, user: UserModel, created_by: str) -> int:
        return await self.user_repository.create_user(user, created_by=created_by)

    async def get_user(
        self,
        cursor: int | None,
        limit: int,
        role_id: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> List[UserItem]:
        rows = await self.user_repository.get_user(
            cursor, limit, role_id, search, sort_by, sort_order
        )
        users = [UserItem(**row) for row in rows]
        return users

    async def get_total_user(
        self,
        role_id: int | None = None,
        search: str | None = None
    ) -> int:
        return await self.user_repository.get_total_user(role_id, search)

    async def get_user_export(
        self,
        role_id: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ):
        async for row in self.user_repository.get_user_export(
            role_id, search, sort_by, sort_order
        ):
            yield UserItem(**row)

    async def get_user_by_id(self, user_id: int) -> UserItem | None:
        row = await self.user_repository.get_user_by_id(user_id)
        if row:
            users = UserItem(**row)
            return users
        return row

    async def lock_user(self, user_id: int) -> bool:
        return await self.user_repository.lock_user(user_id)
