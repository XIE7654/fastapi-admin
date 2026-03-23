"""
岗位服务
"""
from typing import Optional, List, Tuple
from sqlalchemy import select, func
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
    async def get_page(
        db: AsyncSession,
        page_no: int,
        page_size: int,
        name: Optional[str] = None,
        code: Optional[str] = None,
        status: Optional[int] = None,
    ) -> Tuple[List[Post], int]:
        """分页查询岗位"""
        query = select(Post).where(Post.deleted == 0)

        if name:
            query = query.where(Post.name.like(f"%{name}%"))
        if code:
            query = query.where(Post.code.like(f"%{code}%"))
        if status is not None:
            query = query.where(Post.status == status)

        # 查询总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        query = query.order_by(Post.sort.asc())
        query = query.offset((page_no - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        posts = result.scalars().all()

        return list(posts), total

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

    @staticmethod
    async def create(
        db: AsyncSession,
        name: str,
        code: str,
        sort: int = 0,
        remark: str = None,
    ) -> int:
        """创建岗位"""
        # 检查编码是否已存在
        existing = await PostService.get_by_code(db, code)
        if existing:
            raise BusinessException(code=ErrorCode.DATA_EXISTS, message="岗位编码已存在")

        post = Post(
            name=name,
            code=code,
            sort=sort,
            remark=remark,
        )
        db.add(post)
        await db.flush()
        await db.refresh(post)
        return post.id

    @staticmethod
    async def update(
        db: AsyncSession,
        post_id: int,
        name: Optional[str] = None,
        code: Optional[str] = None,
        sort: Optional[int] = None,
        remark: Optional[str] = None,
    ) -> bool:
        """更新岗位"""
        post = await PostService.get_by_id(db, post_id)
        if not post:
            raise BusinessException(code=ErrorCode.DATA_NOT_EXISTS, message="岗位不存在")

        if code is not None:
            # 检查新编码是否已存在
            existing = await PostService.get_by_code(db, code)
            if existing and existing.id != post_id:
                raise BusinessException(code=ErrorCode.DATA_EXISTS, message="岗位编码已存在")
            post.code = code

        if name is not None:
            post.name = name
        if sort is not None:
            post.sort = sort
        if remark is not None:
            post.remark = remark

        await db.flush()
        return True

    @staticmethod
    async def delete(db: AsyncSession, post_id: int) -> bool:
        """删除岗位（软删除）"""
        post = await PostService.get_by_id(db, post_id)
        if not post:
            raise BusinessException(code=ErrorCode.DATA_NOT_EXISTS, message="岗位不存在")

        post.deleted = 1
        await db.flush()
        return True