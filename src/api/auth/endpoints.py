from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from api.auth import deps
from api.deps import get_trace_id
from schema.auth.auth import RefreshRequest
from services.auth.auth_service_interface import AuthServiceInterface

authrouter = APIRouter(prefix="/auth", tags=["auth"])


@authrouter.post(
    "/login",
    status_code=status.HTTP_201_CREATED,
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthServiceInterface = Depends(deps.auth_service),
    trace_id: UUID = Depends(get_trace_id),
):
    return await auth_service.login(
        form_data.username,
        form_data.password,
    )


@authrouter.post("/refresh")
async def refresh(
    payload: RefreshRequest,
    auth_service: AuthServiceInterface = Depends(deps.auth_service),
    trace_id: UUID = Depends(get_trace_id),
):
    return await auth_service.refresh_token(payload.refresh_token)


@authrouter.post("/logout")
async def logout(
    token: str,
    auth_service: AuthServiceInterface = Depends(deps.auth_service),
    trace_id: UUID = Depends(get_trace_id),
):
    return await auth_service.logout(token)
