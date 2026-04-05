from pydantic import BaseModel, Field

from common.schema_types import CamelBaseModel


class TokenResponse(BaseModel):
    access_token: str = Field(..., alias="accessToken")
    refresh_token: str = Field(..., alias="refreshToken")
    token_type: str = "bearer"

    class Config:
        populate_by_name = True


class RefreshRequest(CamelBaseModel):
    refresh_token: str
