from fastapi import Depends

from app.core.security import access_token_cookie
from auth.services import AbstractAuthService, JWTAuthService


def make_auth_service_factory():

    def factory(
        token: str | None = Depends(access_token_cookie),
    ) -> AbstractAuthService:
        return JWTAuthService(token)

    return factory
