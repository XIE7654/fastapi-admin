"""
API 日志服务
"""
from typing import List, Tuple, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.module.infra.model.api_log import ApiAccessLog, ApiErrorLog


class ApiAccessLogService:
    """API访问日志服务"""

    @staticmethod
    async def get_page(
        db: AsyncSession,
        page_no: int,
        page_size: int,
        user_id: Optional[int] = None,
        application_name: Optional[str] = None,
        request_url: Optional[str] = None,
        begin_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        result_code: Optional[int] = None,
    ) -> Tuple[List[ApiAccessLog], int]:
        """分页查询访问日志"""
        query = select(ApiAccessLog)

        if user_id:
            query = query.where(ApiAccessLog.user_id == user_id)
        if application_name:
            query = query.where(ApiAccessLog.application_name == application_name)
        if request_url:
            query = query.where(ApiAccessLog.request_url.like(f"%{request_url}%"))
        if begin_time:
            query = query.where(ApiAccessLog.begin_time >= begin_time)
        if end_time:
            query = query.where(ApiAccessLog.begin_time <= end_time)
        if result_code is not None:
            query = query.where(ApiAccessLog.result_code == result_code)

        # 查询总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        query = query.order_by(ApiAccessLog.id.desc())
        query = query.offset((page_no - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        logs = result.scalars().all()

        return logs, total


class ApiErrorLogService:
    """API异常日志服务"""

    @staticmethod
    async def get_page(
        db: AsyncSession,
        page_no: int,
        page_size: int,
        user_id: Optional[int] = None,
        application_name: Optional[str] = None,
        request_url: Optional[str] = None,
        exception_time: Optional[datetime] = None,
        process_status: Optional[int] = None,
    ) -> Tuple[List[ApiErrorLog], int]:
        """分页查询异常日志"""
        query = select(ApiErrorLog)

        if user_id:
            query = query.where(ApiErrorLog.user_id == user_id)
        if application_name:
            query = query.where(ApiErrorLog.application_name == application_name)
        if request_url:
            query = query.where(ApiErrorLog.request_url.like(f"%{request_url}%"))
        if exception_time:
            query = query.where(ApiErrorLog.exception_time >= exception_time)
        if process_status is not None:
            query = query.where(ApiErrorLog.process_status == process_status)

        # 查询总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        query = query.order_by(ApiErrorLog.id.desc())
        query = query.offset((page_no - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        logs = result.scalars().all()

        return logs, total

    @staticmethod
    async def update_status(db: AsyncSession, id: int, process_status: int) -> bool:
        """更新异常日志处理状态"""
        result = await db.execute(select(ApiErrorLog).where(ApiErrorLog.id == id))
        log = result.scalar_one_or_none()
        if not log:
            return False

        log.process_status = process_status
        log.process_time = datetime.now()
        await db.commit()
        return True