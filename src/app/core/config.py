from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    admin_role_ids: List[int]
    payment_role_ids: List[int]
    evaluation_role_ids: List[int]
    allowed_extensions: List[str]
    allowed_image_extensions: List[str]
    allowed_content_types: List[str]
    allowed_pdf_extension: List[str]
    allowed_pdf_content_type: List[str]
    max_file_size: int
    max_image_size: int
    max_pdf_size: int
    application_env: str
    s3_bucket_name: str
    error_s3_bucket_name: str
    evaluation_photos_s3_bucket_name: str
    stockin_s3_bucket_name: str
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
