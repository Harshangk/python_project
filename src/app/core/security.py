from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, Response, status
from fastapi.security import APIKeyCookie
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.constant import (
    ACCESS_TOKEN_COOKIE_NAME,
    ACCESS_TOKEN_COOKIE_PATH,
    REFRESH_TOKEN_COOKIE_NAME,
    REFRESH_TOKEN_COOKIE_PATH,
)
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


access_token_cookie = APIKeyCookie(name=ACCESS_TOKEN_COOKIE_NAME, auto_error=False)


def _cookie_secure() -> bool:
    return settings.application_env.lower() not in {"local", "dev", "development"}


def _cookie_samesite() -> str:
    return "none" if _cookie_secure() else "lax"


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str | None = None,
) -> None:
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        max_age=settings.access_token_expire_minutes,
        httponly=True,
        secure=_cookie_secure(),
        samesite=_cookie_samesite(),
        path=ACCESS_TOKEN_COOKIE_PATH,
    )

    if refresh_token:
        response.set_cookie(
            key=REFRESH_TOKEN_COOKIE_NAME,
            value=refresh_token,
            max_age=settings.refresh_token_expire_minutes,
            httponly=True,
            secure=_cookie_secure(),
            samesite=_cookie_samesite(),
            path=REFRESH_TOKEN_COOKIE_PATH,
        )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        path=ACCESS_TOKEN_COOKIE_PATH,
        secure=_cookie_secure(),
        samesite=_cookie_samesite(),
        httponly=True,
    )
    response.delete_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        path=REFRESH_TOKEN_COOKIE_PATH,
        secure=_cookie_secure(),
        samesite=_cookie_samesite(),
        httponly=True,
    )


# -------------------------
# Password utilities
# -------------------------


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# -------------------------
# Token creation
# -------------------------


def create_access_token(data: dict) -> str:

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def create_refresh_token(data: dict) -> str:

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=settings.refresh_token_expire_minutes
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt


# -------------------------
# Decode token
# -------------------------


def decode_token(token: str):

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        return payload

    except JWTError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


# -------------------------
# Current user dependency
# -------------------------


async def get_current_user(token: str | None = Depends(access_token_cookie)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    payload = decode_token(token)

    username: str | None = payload.get("user_name")

    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    return username
