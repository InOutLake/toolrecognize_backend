from __future__ import annotations

from typing import Annotated, Any, Optional

import aioboto3
from botocore.utils import ClientError
from fastapi import Depends

from src.core import SETTINGS


class AsyncS3Repository:
    def __init__(self, *, bucket: Optional[str] = None) -> None:
        self._bucket = bucket or SETTINGS.s3_bucket

    def _session(self) -> aioboto3.Session:
        return aioboto3.Session()

    def _client(self):
        return self._session().client(
            "s3",
            endpoint_url=SETTINGS.s3_endpoint_url,
            aws_access_key_id=SETTINGS.s3_access_key,
            aws_secret_access_key=SETTINGS.s3_secret_key,
            region_name=SETTINGS.s3_region,
        )

    async def init_bucket(self) -> None:
        async with self._client() as s3:  # type: ignore
            try:
                await s3.head_bucket(Bucket=self._bucket)
                print(f"Bucket '{self._bucket}' already exists.")
            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                if error_code == "404":
                    print(f"Bucket '{self._bucket}' does not exist. Creating...")
                    await s3.create_bucket(Bucket=self._bucket)
                    print(f"Bucket '{self._bucket}' created successfully.")
                else:
                    raise

    async def upload_file(
        self, *, key: str, data: bytes, content_type: str | None = None
    ) -> str:
        async with self._client() as s3:  # type: ignore
            extra_args: dict[str, Any] = {}
            if content_type:
                extra_args["ContentType"] = content_type
            await s3.put_object(Bucket=self._bucket, Key=key, Body=data, **extra_args)
        return key

    async def delete_file(self, *, key: str) -> None:
        async with self._client() as s3:  # type: ignore
            await s3.delete_object(Bucket=self._bucket, Key=key)

    async def generate_presigned_url(
        self, *, key: str, expires_in_seconds: int = 3600
    ) -> str:
        async with self._client() as s3:  # type: ignore
            url = await s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": self._bucket, "Key": key},
                ExpiresIn=expires_in_seconds,
            )
            return url


def get_s3_storage() -> AsyncS3Repository:
    return AsyncS3Repository()


AsyncS3RepositoryDep = Annotated[AsyncS3Repository, Depends(get_s3_storage)]
