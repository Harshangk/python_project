from datetime import datetime
from enum import Enum
from typing import List, Optional

from common.schema_types import CamelBaseModel
from api.user.example import USER
from model.user import user as UserModel


class Response(CamelBaseModel):
    id: int
    message: str


class CreateUser(CamelBaseModel):
    role: int
    user_name: str
    password: str

    class config:
        schema_extra = {"example": USER}
        orm_mode = True

    def to_model(self) -> UserModel.User:
        return UserModel.User(
            role=self.role,
            user_name=self.user_name,
            password=self.password,
            created_by=None,
        )


user_obj = CreateUser.model_validate(USER)


class UserItem(CamelBaseModel):
    id: int
    user_name: str
    role_id: int
    role: str
    last_login: Optional[datetime] = None
    login_at: Optional[datetime] = None
    created_at: datetime
    created_by: str
    expiry_at: Optional[datetime] = None
    is_lock: bool
    is_active: bool


class UserList(CamelBaseModel):
    total: int
    limit: int
    next: Optional[str]
    items: List[UserItem]


class UserSortBy(str, Enum):
    id = "id"
    user_name = "user_name"
    role = "role"
