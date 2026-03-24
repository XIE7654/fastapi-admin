"""
操作日志服务
"""
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.module.system.model.operate_log import OperateLog
from app.module.system.model.user import User
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
        success: bool = True,
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
            success=success,
        )
        db.add(log)
        await db.flush()
        return log

    @staticmethod
    async def get_list(db: AsyncSession, query: OperateLogPageQuery) -> Tuple[List[dict], int]:
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

        # 分页查询，关联 User 表获取用户昵称
        result = await db.execute(
            select(OperateLog, User.nickname)
            .outerjoin(User, OperateLog.user_id == User.id)
            .where(and_(*conditions))
            .order_by(OperateLog.id.desc())
            .offset(query.offset)
            .limit(query.limit)
        )
        rows = result.all()

        # 组装结果，添加 user_name 字段
        logs = []
        for row in rows:
            log = row[0]
            user_name = row[1]
            log_dict = {
                "id": log.id,
                "trace_id": log.trace_id,
                "user_id": log.user_id,
                "user_name": user_name,
                "user_type": log.user_type,
                "type": log.type,
                "sub_type": log.sub_type,
                "biz_id": log.biz_id,
                "action": log.action,
                "extra": log.extra,
                "request_method": log.request_method,
                "request_url": log.request_url,
                "user_ip": log.user_ip,
                "user_agent": log.user_agent,
                "create_time": log.create_time,
            }
            logs.append(log_dict)

        return logs, total

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