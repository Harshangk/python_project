from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str | None = None
    application_env: str | None = None
    s3_access_key_id: str | None = None
    s3_region_name: str | None = None
    s3_secret_access_key: str | None = None
    s3_endpoint_url: str | None = None
    s3_bucket_name: str | None = None
    SECRET_KEY: str = "supersecret"
    ALGORITHM: str = "HS256"
    access_token_expire_minutes: int | None = None
    refresh_token_expire_minutes: int | None = None

    class Config:
        env_file = ".env"


settings = Settings()
