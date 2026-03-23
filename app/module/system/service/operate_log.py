"""
操作日志服务
"""
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.system.model.operate_log import OperateLog
from app.module.system.schema.log import OperateLogPageQuery
from app.common.utils import generate_snowflake_id


class OperateLogService:
    """操作日志服务"""

    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: int,
        user_type: int,
        type: str,
        sub_type: str,
        biz_id: int = 0,
        action: str = None,
        extra: str = None,
        request_method: str = None,
        request_url: str = None,
        user_ip: str = None,
        user_agent: str = None,
        tenant_id: int = None,
    ) -> OperateLog:
        """创建操作日志"""
        log = OperateLog(
            trace_id=str(generate_snowflake_id()),
            user_id=user_id,
            user_type=user_type,
            type=type,
            sub_type=sub_type,
            biz_id=biz_id,
            action=action,
            extra=extra,
            request_method=request_method,
            request_url=request_url,
            user_ip=user_ip,
            user_agent=user_agent,
            tenant_id=tenant_id or 1,
        )
        db.add(log)
        await db.flush()
        return log

    @staticmethod
    async def get_list(db: AsyncSession, query: OperateLogPageQuery) -> Tuple[List[OperateLog], int]:
        """分页查询操作日志"""
        conditions = [OperateLog.deleted == 0]

        if query.user_id:
            conditions.append(OperateLog.user_id == query.user_id)
        if query.type:
            conditions.append(OperateLog.type.like(f"%{query.type}%"))
        if query.sub_type:
            conditions.append(OperateLog.sub_type.like(f"%{query.sub_type}%"))
        if query.create_time and len(query.create_time) == 2:
            conditions.append(OperateLog.create_time.between(query.create_time[0], query.create_time[1]))

        # 查询总数
        count_query = select(func.count()).select_from(OperateLog).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        result = await db.execute(
            select(OperateLog)
            .where(and_(*conditions))
            .order_by(OperateLog.id.desc())
            .offset(query.offset)
            .limit(query.limit)
        )
        logs = result.scalars().all()

        return list(logs), total

    @staticmethod
    async def delete_by_ids(db: AsyncSession, log_ids: List[int]) -> int:
        """批量删除操作日志"""
        count = 0
        for log_id in log_ids:
            result = await db.execute(
                select(OperateLog).where(OperateLog.id == log_id)
            )
            log = result.scalar_one_or_none()
            if log:
                log.deleted = 1
                count += 1
        await db.flush()
        return count