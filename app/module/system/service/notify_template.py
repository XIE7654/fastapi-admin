"""
站内信模板服务
"""
from typing import Optional, List, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.system.model.notify import NotifyTemplate


class NotifyTemplateService:
    """站内信模板服务"""

    @staticmethod
    async def get_by_id(db: AsyncSession, template_id: int) -> Optional[NotifyTemplate]:
        """根据ID获取站内信模板"""
        result = await db.execute(
            select(NotifyTemplate).where(NotifyTemplate.id == template_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession) -> List[NotifyTemplate]:
        """获取所有站内信模板"""
        result = await db.execute(
            select(NotifyTemplate).order_by(NotifyTemplate.id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_page(
        db: AsyncSession,
        page_no: int = 1,
        page_size: int = 10,
        name: str = None,
        code: str = None,
        status: int = None,
        type: int = None,
    ) -> Tuple[List[NotifyTemplate], int]:
        """分页获取站内信模板"""
        conditions = []

        if name:
            conditions.append(NotifyTemplate.name.like(f"%{name}%"))
        if code:
            conditions.append(NotifyTemplate.code.like(f"%{code}%"))
        if status is not None:
            conditions.append(NotifyTemplate.status == status)
        if type is not None:
            conditions.append(NotifyTemplate.type == type)

        # 查询总数
        count_query = select(func.count(NotifyTemplate.id))
        if conditions:
            count_query = count_query.where(*conditions)
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 查询列表
        query = select(NotifyTemplate)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(NotifyTemplate.id.desc())
        query = query.offset((page_no - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total


class NotifyMessageServiceExt:
    """站内信消息扩展服务"""

    @staticmethod
    async def get_page(
        db: AsyncSession,
        page_no: int = 1,
        page_size: int = 10,
        user_id: int = None,
        user_type: int = None,
        read_status: int = None,
        template_code: str = None,
        template_type: int = None,
        create_time: list = None,
    ) -> Tuple[List, int]:
        """分页获取站内信消息"""
        from app.module.system.model.notify import NotifyMessage

        conditions = []

        if user_id is not None:
            conditions.append(NotifyMessage.user_id == user_id)
        if user_type is not None:
            conditions.append(NotifyMessage.user_type == user_type)
        if read_status is not None:
            conditions.append(NotifyMessage.read_status == read_status)
        if template_code:
            conditions.append(NotifyMessage.template_code.like(f"%{template_code}%"))
        if template_type is not None:
            conditions.append(NotifyMessage.template_type == template_type)
        if create_time and len(create_time) == 2:
            conditions.append(NotifyMessage.create_time.between(create_time[0], create_time[1]))

        # 查询总数
        count_query = select(func.count(NotifyMessage.id))
        if conditions:
            count_query = count_query.where(*conditions)
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 查询列表
        query = select(NotifyMessage)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(NotifyMessage.id.desc())
        query = query.offset((page_no - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total