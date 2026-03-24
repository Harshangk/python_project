import os
import pathlib
import shutil
from abc import ABC, abstractmethod
from datetime import date
from typing import IO, Iterator

from botocore.exceptions import (ClientError, ParamValidationError,
                                 ValidationError)
from mypy_boto3_s3 import S3ServiceResource

from app.core.config import settings


class AbstractFileStorage(ABC):
    @abstractmethod
    def files_list(self, prefix_path: pathlib.Path | None = None) -> Iterator[str]: ...

    @abstractmethod
    def download_file(self, file_key: str, file_obj: IO[bytes]) -> None: ...

    @abstractmethod
    def move_file(self, source_path: str, target_path: str) -> None: ...

    @abstractmethod
    def upload_file(
        self,
        filename: str,
        file_path: str | None = None,
        file_obj: bytes | None = None,
        content_type: str | None = None,
    ) -> str: ...

    @abstractmethod
    def generate_file_url(self, file_key: str) -> str: ...

    @abstractmethod
    def file_exists(self, file_key) -> bool: ...

    @abstractmethod
    def download_file_to_local(self, filename: str) -> str | None: ...


class FileKeyNotFound(Exception): ...


class S3FileStorage(AbstractFileStorage):
    page_size: int = 20
    expiry: int = 3600

    def __init__(self, client: S3ServiceResource, bucket_name: str):
        self.client = client
        self.bucket = self.client.Bucket(bucket_name)

    def files_list(self, prefix_path: pathlib.Path | None = None) -> Iterator[str]:
        query = self.bucket.objects
        if prefix_path:
            query = query.filter(Prefix=str(prefix_path))
        for s3_file in query.all().page_size(self.page_size):
            yield s3_file.key

    def download_file(self, file_key: str, file_obj: IO[bytes]) -> None:
        self.bucket.download_fileobj(Key=file_key, Fileobj=file_obj)

    def move_file(self, source_path: str, target_path: str) -> None:
        self.copy_file(source_path, target_path)
        self.delete_file(source_path)

    def copy_file(self, source_path: str, target_path: str) -> None:
        self.client.Object(self.bucket.name, target_path).copy_from(
            CopySource=f"{self.bucket.name}/{source_path}"
        )

    def delete_file(self, source_path: str) -> None:
        self.bucket.Object(key=source_path).delete()

    def upload_file(
        self,
        filename: str,
        file_path: str | None = None,
        file_obj: bytes | None = None,
        content_type: str | None = None,
    ) -> str:
        file_key = f"{date.today()}/{filename}"
        if file_path is not None:
            self.bucket.upload_file(file_path, file_key)
            os.remove(file_path)
        elif file_obj is not None:
            if content_type:
                self.bucket.put_object(
                    Key=filename, Body=file_obj, ContentType=content_type
                )
            else:
                self.bucket.put_object(Key=file_key, Body=file_obj)
        return file_key

    def generate_file_url(self, file_key: str) -> str:
        return self.client.meta.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket.name, "Key": file_key},
            ExpiresIn=self.expiry,
        )

    def file_exists(self, file_key: str) -> bool:
        # https://stackoverflow.com/a/44979500
        try:
            self.client.Object(self.bucket.name, file_key).load()
        except ClientError as e:
            if int(e.response["Error"]["Code"]) == 404:
                return False
            else:
                raise e
        except (ValidationError, ParamValidationError):
            return False
        return True

    def download_file_to_local(self, filename: str) -> str | None:
        try:
            filename_only = filename.split("/")[-1]
            path = os.path.abspath(filename_only)
            path_to_save_file = f"{os.path.dirname(path)}/{filename_only}"
            self.bucket.download_file(filename, path_to_save_file)
            return path_to_save_file
        except ClientError as e:
            if int(e.response["Error"]["Code"]) == 404:
                return None
            else:
                raise e
        except (ValidationError, ParamValidationError):
            return None


class LocalFileStorage(AbstractFileStorage):
    def __init__(self, root_path: str):
        self.root_path = pathlib.Path(root_path)

    def files_list(self, prefix_path: pathlib.Path | None = None) -> Iterator[str]:
        source_dir = pathlib.Path(self.root_path)
        if prefix_path:
            source_dir /= prefix_path
        for path, subdirs, files in os.walk(source_dir):
            for name in files:
                full_path = pathlib.Path(path, name)
                yield os.path.relpath(full_path, self.root_path)

    def download_file(self, file_key: str, file_obj: IO[bytes]) -> None:
        with open(self.root_path / file_key, "rb") as read_file:
            lines = read_file.readlines()
            file_obj.writelines(lines)

    def move_file(self, source_path: str, target_path: str) -> None:
        target_dir = pathlib.Path(self.root_path, target_path).parent
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(self.root_path / source_path, self.root_path / target_path)

    def upload_file(
        self,
        filename: str,
        file_path: str | None = None,
        file_obj: bytes | None = None,
        content_type: str | None = None,
    ) -> str:
        target_path = pathlib.Path(self.root_path, filename)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if file_path is not None:
            with open(file_path, "rb") as f:
                with open(target_path, "wb") as dest:
                    dest.write(f.read())
                    os.remove(file_path)

        elif file_obj is not None:
            with open(target_path, "wb") as dest:
                dest.write(file_obj)
        return filename

    def generate_file_url(self, file_key: str) -> str:
        file_path = self.root_path / file_key
        return f"http://{settings.APP_HOST}:{settings.APP_PORT}/{file_path}"

    def file_exists(self, file_key: str) -> bool:
        file_path = self.root_path / file_key
        return file_path.exists() and file_path.is_file()

    def download_file_to_local(self, filename: str) -> str | None:
        try:
            filename_only = filename.split("/")[-1]
            return filename_only
        except ClientError:
            return None
