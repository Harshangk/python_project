from abc import ABC, abstractmethod

from jose import JWTError, jwt
from pydantic import ValidationError

from app.core.config import settings
from auth.dto import (
    Actor,
    AuthenticatedActor,
    AuthenticatedUser,
    BaseUser,
    Service,
    User,
)
from auth.exceptions import Unauthorized


class AbstractAuthService(ABC):
    @property
    @abstractmethod
    def current_user(self) -> Actor: ...

    @property
    def authenticated_user(self) -> AuthenticatedUser:
        if not isinstance(self.current_user, AuthenticatedUser):
            raise Unauthorized()
        return self.current_user

    @property
    def authenticated_service(self) -> Service:
        if not isinstance(self.current_user, Service):
            raise Unauthorized()
        return self.current_user

    @property
    def authenticated_actor(self) -> AuthenticatedActor:
        if not isinstance(self.current_user, (AuthenticatedUser, Service)):
            raise Unauthorized()
        return self.current_user


class FakeAuthService(AbstractAuthService):
    def __init__(self, user: User | None = None):
        self.user = user or AuthenticatedUser(
            id=1,
            userName="user@example.com",
            role_id=1,
            role="Admin",
            lastLogin="2026-03-14T13:05:03.859281",
            loginAt="2026-03-14T13:05:03.859281",
            createdAt="2026-03-14T13:05:03.859281",
            createdBy="harshang",
            expiryAt="2026-03-14T13:05:03.859281",
            isLock=False,
            isActive=BaseUser(is_active=True),
        )

    @property
    def current_user(self) -> Actor:
        return self.user


class JWTAuthService(AbstractAuthService):
    def __init__(self, token: str):
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
        except JWTError:
            raise Unauthorized()

        username = payload.get("user_name")

        if not username:
            raise Unauthorized()

        try:
            self.user = AuthenticatedUser(**payload)
        except ValidationError:
            raise Unauthorized()

    @property
    def current_user(self) -> Actor:
        return self.user
