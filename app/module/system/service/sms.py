"""
短信渠道服务
"""
from typing import Optional, List, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.system.model.sms import SmsChannel


class SmsChannelService:
    """短信渠道服务"""

    @staticmethod
    async def get_by_id(db: AsyncSession, channel_id: int) -> Optional[SmsChannel]:
        """根据ID获取短信渠道"""
        result = await db.execute(
            select(SmsChannel).where(SmsChannel.id == channel_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession) -> List[SmsChannel]:
        """获取所有短信渠道"""
        result = await db.execute(
            select(SmsChannel).order_by(SmsChannel.id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_page(
        db: AsyncSession,
        page_no: int = 1,
        page_size: int = 10,
        status: int = None,
        signature: str = None,
        code: str = None,
    ) -> Tuple[List[SmsChannel], int]:
        """分页获取短信渠道"""
        conditions = []

        if status is not None:
            conditions.append(SmsChannel.status == status)
        if signature:
            conditions.append(SmsChannel.signature.like(f"%{signature}%"))
        if code:
            conditions.append(SmsChannel.code.like(f"%{code}%"))

        # 查询总数
        count_query = select(func.count(SmsChannel.id))
        if conditions:
            count_query = count_query.where(*conditions)
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 查询列表
        query = select(SmsChannel)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(SmsChannel.id.desc())
        query = query.offset((page_no - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total


class SmsTemplateService:
    """短信模板服务"""

    @staticmethod
    async def get_by_id(db: AsyncSession, template_id: int) -> Optional[dict]:
        """根据ID获取短信模板"""
        from app.module.system.model.sms import SmsTemplate
        result = await db.execute(
            select(SmsTemplate).where(SmsTemplate.id == template_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_page(
        db: AsyncSession,
        page_no: int = 1,
        page_size: int = 10,
        status: int = None,
        name: str = None,
        code: str = None,
        channel_id: int = None,
    ) -> Tuple[List, int]:
        """分页获取短信模板"""
        from app.module.system.model.sms import SmsTemplate

        conditions = []

        if status is not None:
            conditions.append(SmsTemplate.status == status)
        if name:
            conditions.append(SmsTemplate.name.like(f"%{name}%"))
        if code:
            conditions.append(SmsTemplate.code.like(f"%{code}%"))
        if channel_id is not None:
            conditions.append(SmsTemplate.channel_id == channel_id)

        # 查询总数
        count_query = select(func.count(SmsTemplate.id))
        if conditions:
            count_query = count_query.where(*conditions)
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 查询列表
        query = select(SmsTemplate)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(SmsTemplate.id.desc())
        query = query.offset((page_no - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total