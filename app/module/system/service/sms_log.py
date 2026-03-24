"""
短信日志服务
"""
from typing import Optional, List, Tuple
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.system.model.sms import SmsLog


class SmsLogService:
    """短信日志服务"""

    @staticmethod
    async def get_by_id(db: AsyncSession, log_id: int) -> Optional[SmsLog]:
        """根据ID获取短信日志"""
        result = await db.execute(
            select(SmsLog).where(SmsLog.id == log_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(
        db: AsyncSession,
        channel_id: int = None,
        template_id: int = None,
        mobile: str = None,
        send_status: int = None,
        receive_status: int = None,
        send_time: List[datetime] = None,
        receive_time: List[datetime] = None,
    ) -> List[SmsLog]:
        """获取短信日志列表（不分页，用于导出）"""
        conditions = []

        if channel_id is not None:
            conditions.append(SmsLog.channel_id == channel_id)
        if template_id is not None:
            conditions.append(SmsLog.template_id == template_id)
        if mobile:
            conditions.append(SmsLog.mobile.like(f"%{mobile}%"))
        if send_status is not None:
            conditions.append(SmsLog.send_status == send_status)
        if receive_status is not None:
            conditions.append(SmsLog.receive_status == receive_status)
        if send_time and len(send_time) == 2:
            conditions.append(SmsLog.send_time.between(send_time[0], send_time[1]))
        if receive_time and len(receive_time) == 2:
            conditions.append(SmsLog.receive_time.between(receive_time[0], receive_time[1]))

        # 查询列表
        query = select(SmsLog)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(SmsLog.id.desc())

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_page(
        db: AsyncSession,
        page_no: int = 1,
        page_size: int = 10,
        channel_id: int = None,
        template_id: int = None,
        mobile: str = None,
        send_status: int = None,
        receive_status: int = None,
        send_time: List[datetime] = None,
        receive_time: List[datetime] = None,
    ) -> Tuple[List[SmsLog], int]:
        """分页获取短信日志"""
        conditions = []

        if channel_id is not None:
            conditions.append(SmsLog.channel_id == channel_id)
        if template_id is not None:
            conditions.append(SmsLog.template_id == template_id)
        if mobile:
            conditions.append(SmsLog.mobile.like(f"%{mobile}%"))
        if send_status is not None:
            conditions.append(SmsLog.send_status == send_status)
        if receive_status is not None:
            conditions.append(SmsLog.receive_status == receive_status)
        if send_time and len(send_time) == 2:
            conditions.append(SmsLog.send_time.between(send_time[0], send_time[1]))
        if receive_time and len(receive_time) == 2:
            conditions.append(SmsLog.receive_time.between(receive_time[0], receive_time[1]))

        # 查询总数
        count_query = select(func.count(SmsLog.id))
        if conditions:
            count_query = count_query.where(*conditions)
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 查询列表
        query = select(SmsLog)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(SmsLog.id.desc())
        query = query.offset((page_no - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total