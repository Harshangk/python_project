from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    allowed_extensions: List[str]
    max_file_size: int
    application_env: str
    s3_bucket_name: str
    error_s3_bucket_name: str
    s3_access_key_id: str
    s3_region_name: str
    s3_secret_access_key: str
    s3_endpoint_url: str
    SECRET_KEY: str = "supersecret"
    ALGORITHM: str = "HS256"
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int

    class Config:
        env_file = ".env"


settings = Settings()
