"""
文件存储扩展
"""
import os
from abc import ABC, abstractmethod
from typing import Optional, BinaryIO
from pathlib import Path
import aiofiles
from datetime import datetime

from app.config import settings
from app.common.utils import generate_uuid


class StorageBackend(ABC):
    """存储后端抽象基类"""

    @abstractmethod
    async def save(self, file: BinaryIO, filename: str, path: str = "") -> str:
        """保存文件，返回访问URL"""
        pass

    @abstractmethod
    async def delete(self, path: str) -> bool:
        """删除文件"""
        pass

    @abstractmethod
    async def exists(self, path: str) -> bool:
        """检查文件是否存在"""
        pass

    @abstractmethod
    async def get_url(self, path: str) -> str:
        """获取文件访问URL"""
        pass


class LocalStorage(StorageBackend):
    """本地文件存储"""

    def __init__(self, base_path: str = "uploads", base_url: str = "/uploads"):
        self.base_path = Path(base_path)
        self.base_url = base_url
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_date_path(self) -> str:
        """获取日期路径"""
        now = datetime.now()
        return f"{now.year}/{now.month:02d}/{now.day:02d}"

    async def save(self, file: BinaryIO, filename: str, path: str = "") -> str:
        """保存文件"""
        # 生成唯一文件名
        ext = os.path.splitext(filename)[1]
        new_filename = f"{generate_uuid()}{ext}"

        # 构建存储路径
        date_path = self._get_date_path()
        relative_path = os.path.join(path, date_path, new_filename) if path else os.path.join(date_path, new_filename)
        full_path = self.base_path / relative_path

        # 创建目录
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # 写入文件
        async with aiofiles.open(full_path, "wb") as f:
            content = file.read()
            await f.write(content)

        return await self.get_url(relative_path)

    async def delete(self, path: str) -> bool:
        """删除文件"""
        full_path = self.base_path / path
        if full_path.exists():
            full_path.unlink()
            return True
        return False

    async def exists(self, path: str) -> bool:
        """检查文件是否存在"""
        return (self.base_path / path).exists()

    async def get_url(self, path: str) -> str:
        """获取文件访问URL"""
        return f"{self.base_url}/{path}"


class S3Storage(StorageBackend):
    """S3存储（兼容MinIO等）"""

    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        region: str = "us-east-1",
    ):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket
        self.region = region
        self._client = None

    @property
    def client(self):
        """懒加载S3客户端"""
        if self._client is None:
            import boto3
            self._client = boto3.client(
                "s3",
                endpoint_url=self.endpoint,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region,
            )
        return self._client

    async def save(self, file: BinaryIO, filename: str, path: str = "") -> str:
        """保存文件到S3"""
        ext = os.path.splitext(filename)[1]
        new_filename = f"{generate_uuid()}{ext}"

        date_path = self._get_date_path()
        key = f"{path}/{date_path}/{new_filename}" if path else f"{date_path}/{new_filename}"

        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=file.read(),
        )

        return await self.get_url(key)

    async def delete(self, path: str) -> bool:
        """从S3删除文件"""
        try:
            self.client.delete_object(Bucket=self.bucket, Key=path)
            return True
        except Exception:
            return False

    async def exists(self, path: str) -> bool:
        """检查S3文件是否存在"""
        try:
            self.client.head_object(Bucket=self.bucket, Key=path)
            return True
        except Exception:
            return False

    async def get_url(self, path: str) -> str:
        """获取S3文件URL"""
        return f"{self.endpoint}/{self.bucket}/{path}"


def get_storage() -> StorageBackend:
    """获取存储后端实例"""
    # 根据配置返回不同的存储后端
    # TODO: 从配置读取
    return LocalStorage()