from uuid import UUID

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from api.auth import deps
from api.deps import get_trace_id
from app.core.security import (
    REFRESH_TOKEN_COOKIE_NAME,
    clear_auth_cookies,
    set_auth_cookies,
)
from services.auth.auth_service_interface import AuthServiceInterface

authrouter = APIRouter(prefix="/auth", tags=["auth"])


@authrouter.post(
    "/login",
    status_code=status.HTTP_201_CREATED,
)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthServiceInterface = Depends(deps.auth_service),
    trace_id: UUID = Depends(get_trace_id),
):
    tokens = await auth_service.login(
        form_data.username,
        form_data.password,
    )
    set_auth_cookies(
        response,
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
    )
    return {"message": "Login successful"}


@authrouter.post("/refresh")
async def refresh(
    response: Response,
    refresh_token: str | None = Cookie(None, alias=REFRESH_TOKEN_COOKIE_NAME),
    auth_service: AuthServiceInterface = Depends(deps.auth_service),
    trace_id: UUID = Depends(get_trace_id),
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    tokens = await auth_service.refresh_token(refresh_token)
    set_auth_cookies(response, access_token=tokens["access_token"])
    return {"message": "Token refreshed"}


@authrouter.post("/logout")
async def logout(
    response: Response,
    auth_service: AuthServiceInterface = Depends(deps.auth_service),
    trace_id: UUID = Depends(get_trace_id),
):
    result = await auth_service.logout()
    clear_auth_cookies(response)
    return result
