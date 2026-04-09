from fastapi import HTTPException
from jose import JWTError, jwt

from app.core.config import settings
from app.core.security import (create_access_token, create_refresh_token,
                               verify_password)
from auth.dto import AuthenticatedUser, BaseUser
from repository.auth.auth_repository_interface import AuthRepositoryInterface
from services.auth.auth_service_interface import AuthServiceInterface


class AuthService(AuthServiceInterface):
    def __init__(self, auth_repository: AuthRepositoryInterface) -> None:
        self.auth_repository = auth_repository

    async def login(self, username: str, password: str):
        user_info = await self.auth_repository.login(username)
        if not user_info:
            raise HTTPException(status_code=401, detail="Invalid username")

        if not verify_password(password, user_info.password):
            raise HTTPException(status_code=401, detail="Invalid password")

        user = await self.auth_repository.last_login(username)

        auth_user = AuthenticatedUser(
            id=user.id,
            user_name=user.user_name,
            role_id=user.role_id,
            role=user.role,
            last_login=user.last_login,
            login_at=user.login_at,
            created_at=user.created_at,
            created_by=user.created_by,
            expiry_at=user.expiry_at,
            is_lock=user.is_lock,
            is_active=BaseUser(is_active=user.is_active),
        )
        user_dict = auth_user.model_dump()
        for field in ["created_at", "expiry_at", "last_login", "login_at"]:
            if user_dict.get(field):
                user_dict[field] = user_dict[field].isoformat()
        # generate tokens
        access_token = create_access_token(user_dict)
        refresh_token = create_refresh_token(user_dict)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            # "user": auth_user,  # include user info in response if needed
        }

    async def refresh_token(self, refresh_token: str):

        try:
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )

            username = payload.get("sub")

            if not username:
                raise HTTPException(status_code=401, detail="Invalid refresh token")

            # ideally fetch user from DB again if needed
            access_token = create_access_token(payload)
            return {"access_token": access_token}
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

    async def logout(self, token: str):

        # For now stateless logout
        # Later we can add token blacklist

        return {"message": "Logout successful"}
