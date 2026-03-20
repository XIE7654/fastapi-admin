"""
岗位服务
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.system.model.post import Post
from app.core.exceptions import BusinessException, ErrorCode


class PostService:
    """岗位服务"""

    @staticmethod
    async def get_by_id(db: AsyncSession, post_id: int) -> Optional[Post]:
        """根据ID获取岗位"""
        result = await db.execute(
            select(Post).where(Post.id == post_id, Post.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_code(db: AsyncSession, code: str) -> Optional[Post]:
        """根据编码获取岗位"""
        result = await db.execute(
            select(Post).where(Post.code == code, Post.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession) -> List[Post]:
        """获取所有岗位"""
        result = await db.execute(
            select(Post)
            .where(Post.deleted == 0)
            .order_by(Post.sort.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_by_ids(db: AsyncSession, post_ids: List[int]) -> List[Post]:
        """根据ID列表获取岗位"""
        if not post_ids:
            return []
        result = await db.execute(
            select(Post)
            .where(Post.id.in_(post_ids), Post.deleted == 0)
        )
        return list(result.scalars().all())