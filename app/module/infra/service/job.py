"""
定时任务服务
"""
from typing import List, Tuple, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.module.infra.model.job import Job, JobLog


class JobService:
    """定时任务服务"""

    @staticmethod
    async def get_page(
        db: AsyncSession,
        page_no: int,
        page_size: int,
        name: Optional[str] = None,
        status: Optional[int] = None,
        handler_name: Optional[str] = None,
    ) -> Tuple[List[Job], int]:
        """分页查询定时任务"""
        query = select(Job)

        if name:
            query = query.where(Job.name.like(f"%{name}%"))
        if status is not None:
            query = query.where(Job.status == status)
        if handler_name:
            query = query.where(Job.handler_name.like(f"%{handler_name}%"))

        # 查询总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        query = query.order_by(Job.id.desc())
        query = query.offset((page_no - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        jobs = result.scalars().all()

        return jobs, total

    @staticmethod
    async def get_by_id(db: AsyncSession, id: int) -> Optional[Job]:
        """根据ID获取任务"""
        result = await db.execute(select(Job).where(Job.id == id))
        return result.scalar_one_or_none()


class JobLogService:
    """定时任务日志服务"""

    @staticmethod
    async def get_page(
        db: AsyncSession,
        page_no: int,
        page_size: int,
        job_id: Optional[int] = None,
        handler_name: Optional[str] = None,
    ) -> Tuple[List[JobLog], int]:
        """分页查询任务日志"""
        query = select(JobLog)

        if job_id:
            query = query.where(JobLog.job_id == job_id)
        if handler_name:
            query = query.where(JobLog.handler_name.like(f"%{handler_name}%"))

        # 查询总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        query = query.order_by(JobLog.id.desc())
        query = query.offset((page_no - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        logs = result.scalars().all()

        return logs, total