from __future__ import annotations
import io
from typing import BinaryIO

import boto3
from botocore.client import Config

from app.config import settings

s3 = boto3.client(
    "s3",
    endpoint_url=settings.s3_endpoint,
    region_name=settings.s3_region,
    aws_access_key_id=settings.s3_access_key_id,
    aws_secret_access_key=settings.s3_secret_access_key,
    config=Config(signature_version="s3v4"),
)

def upload_bytes(key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
    s3.put_object(Bucket=settings.s3_bucket, Key=key, Body=data, ContentType=content_type)
    return key

def download_bytes(key: str) -> bytes:
    obj = s3.get_object(Bucket=settings.s3_bucket, Key=key)
    return obj["Body"].read()

def public_url(key: str) -> str:
    base = settings.s3_public_base_url.rstrip("/")
    return f"{base}/{settings.s3_bucket}/{key}"

def list_prefix(prefix: str) -> list[str]:
    resp = s3.list_objects_v2(Bucket=settings.s3_bucket, Prefix=prefix)
    return [item["Key"] for item in resp.get("Contents", []) if item["Key"] != prefix]
