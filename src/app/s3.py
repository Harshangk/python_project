from functools import cache

import boto3
from mypy_boto3_s3 import S3ServiceResource

from app.core.config import settings


@cache
def get_s3_client() -> S3ServiceResource:
    config = dict(
        region_name=settings.s3_region_name,
        aws_access_key_id=settings.s3_access_key_id,
        aws_secret_access_key=settings.s3_secret_access_key,
        endpoint_url=settings.s3_endpoint_url,
    )
    if not all(config.values()):
        raise RuntimeError("No S3 configuration provided, set configuration variables")
    return boto3.resource("s3", **config)  # type: ignore
