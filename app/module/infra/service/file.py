"""
文件服务
"""
from typing import List, Tuple, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.module.infra.model.file import File, FileConfig


class FileService:
    """文件服务"""

    @staticmethod
    async def get_page(
        db: AsyncSession,
        page_no: int,
        page_size: int,
        path: Optional[str] = None,
        type: Optional[str] = None,
    ) -> Tuple[List[File], int]:
        """分页查询文件列表"""
        query = select(File)

        if path:
            query = query.where(File.path.like(f"%{path}%"))
        if type:
            query = query.where(File.type == type)

        # 查询总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        query = query.order_by(File.id.desc())
        query = query.offset((page_no - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        files = result.scalars().all()

        return files, total

    @staticmethod
    async def get_by_id(db: AsyncSession, id: int) -> Optional[File]:
        """根据ID获取文件"""
        result = await db.execute(select(File).where(File.id == id))
        return result.scalar_one_or_none()

    @staticmethod
    async def delete(db: AsyncSession, id: int) -> bool:
        """删除文件"""
        result = await db.execute(select(File).where(File.id == id))
        file = result.scalar_one_or_none()
        if not file:
            return False

        await db.delete(file)
        await db.commit()
        return True


class FileConfigService:
    """文件配置服务"""

    @staticmethod
    async def get_all(db: AsyncSession) -> List[FileConfig]:
        """获取所有文件配置"""
        result = await db.execute(select(FileConfig).order_by(FileConfig.id))
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, id: int) -> Optional[FileConfig]:
        """根据ID获取文件配置"""
        result = await db.execute(select(FileConfig).where(FileConfig.id == id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_master(db: AsyncSession) -> Optional[FileConfig]:
        """获取主配置"""
        result = await db.execute(
            select(FileConfig).where(FileConfig.master == 1)
        )
        return result.scalar_one_or_none()