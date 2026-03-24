from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    application_env: str
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
