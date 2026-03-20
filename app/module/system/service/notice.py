"""
通知公告服务
"""
from typing import List, Tuple, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.module.system.model.notice import Notice


class NoticeService:
    """通知公告服务"""

    @staticmethod
    async def create(
        db: AsyncSession,
        title: str,
        content: str,
        type: int,
        status: int = 0,
    ) -> int:
        """创建通知公告"""
        notice = Notice(
            title=title,
            content=content,
            type=type,
            status=status,
        )
        db.add(notice)
        await db.commit()
        await db.refresh(notice)
        return notice.id

    @staticmethod
    async def update(
        db: AsyncSession,
        id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        type: Optional[int] = None,
        status: Optional[int] = None,
    ) -> bool:
        """更新通知公告"""
        result = await db.execute(select(Notice).where(Notice.id == id))
        notice = result.scalar_one_or_none()
        if not notice:
            return False

        if title is not None:
            notice.title = title
        if content is not None:
            notice.content = content
        if type is not None:
            notice.type = type
        if status is not None:
            notice.status = status

        await db.commit()
        return True

    @staticmethod
    async def delete(db: AsyncSession, id: int) -> bool:
        """删除通知公告"""
        result = await db.execute(select(Notice).where(Notice.id == id))
        notice = result.scalar_one_or_none()
        if not notice:
            return False

        await db.delete(notice)
        await db.commit()
        return True

    @staticmethod
    async def get_by_id(db: AsyncSession, id: int) -> Optional[Notice]:
        """根据ID获取通知公告"""
        result = await db.execute(select(Notice).where(Notice.id == id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_page(
        db: AsyncSession,
        page_no: int,
        page_size: int,
        title: Optional[str] = None,
        type: Optional[int] = None,
        status: Optional[int] = None,
    ) -> Tuple[List[Notice], int]:
        """分页查询通知公告"""
        query = select(Notice)

        if title:
            query = query.where(Notice.title.like(f"%{title}%"))
        if type is not None:
            query = query.where(Notice.type == type)
        if status is not None:
            query = query.where(Notice.status == status)

        # 查询总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        query = query.order_by(Notice.id.desc())
        query = query.offset((page_no - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        notices = result.scalars().all()

        return notices, total

    @staticmethod
    async def get_all(db: AsyncSession, status: Optional[int] = None) -> List[Notice]:
        """获取所有通知公告"""
        query = select(Notice)
        if status is not None:
            query = query.where(Notice.status == status)
        query = query.order_by(Notice.id.desc())
        result = await db.execute(query)
        return result.scalars().all()