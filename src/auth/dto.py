from datetime import datetime
from typing import Annotated, Literal, Optional

from pydantic import Field

from common.schema_types import CamelBaseModel


class BaseUser(CamelBaseModel):
    is_active: bool


class Anonymous(BaseUser):
    is_active: Literal[False] = False


class AuthenticatedUser(CamelBaseModel):
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
    is_active: BaseUser

    class Config:
        validate_by_name = True


User = Annotated[Anonymous | AuthenticatedUser, Field(discriminator="is_active")]


class Service(CamelBaseModel):
    is_active: BaseUser
    client_id: str


Actor = User | Service
AuthenticatedActor = AuthenticatedUser | Service
