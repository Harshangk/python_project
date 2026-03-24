from fastapi import Depends

from app.core.security import oauth2_scheme
from auth.services import AbstractAuthService, JWTAuthService


def make_auth_service_factory():

    def factory(
        token: str = Depends(oauth2_scheme),
    ) -> AbstractAuthService:
        return JWTAuthService(token)

    return factory
