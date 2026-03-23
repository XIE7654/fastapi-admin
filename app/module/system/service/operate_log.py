"""
操作日志服务
"""
import json
import time
from typing import Optional, List, Tuple
from datetime import datetime
from functools import wraps
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
        module: str,
        name: str,
        request_method: str,
        request_url: str,
        request_params: dict = None,
        user_id: int = None,
        user_name: str = None,
        user_ip: str = None,
        user_agent: str = None,
        start_time: datetime = None,
        duration: int = None,
        result_code: int = 0,
        result_msg: str = None,
        tenant_id: int = None,
    ) -> OperateLog:
        """创建操作日志"""
        log = OperateLog(
            module=module,
            name=name,
            request_method=request_method,
            request_url=request_url,
            request_params=json.dumps(request_params, ensure_ascii=False) if request_params else None,
            user_id=user_id,
            user_name=user_name,
            user_ip=user_ip,
            user_agent=user_agent,
            start_time=start_time,
            duration=duration,
            result_code=result_code,
            result_msg=result_msg,
            tenant_id=tenant_id or 1,
            trace_id=str(generate_snowflake_id()),
        )
        db.add(log)
        await db.flush()
        return log

    @staticmethod
    async def get_list(db: AsyncSession, query: OperateLogPageQuery) -> Tuple[List[OperateLog], int]:
        """分页查询操作日志"""
        conditions = [OperateLog.deleted == 0]

        if query.module:
            conditions.append(OperateLog.module.like(f"%{query.module}%"))
        if query.user_id:
            conditions.append(OperateLog.user_id == query.user_id)
        if query.user_name:
            conditions.append(OperateLog.user_name.like(f"%{query.user_name}%"))
        if query.type is not None:
            conditions.append(OperateLog.type == query.type)
        if query.result_code is not None:
            conditions.append(OperateLog.result_code == query.result_code)
        if query.start_time and len(query.start_time) == 2:
            conditions.append(OperateLog.start_time.between(query.start_time[0], query.start_time[1]))

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


def log_operation(module: str, name: str, type: int = 0):
    """
    操作日志装饰器

    用法:
        @log_operation(module="用户管理", name="创建用户")
        async def create_user(...):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = datetime.now()
            result_code = 0
            result_msg = "成功"
            result_data = None

            try:
                result = await func(*args, **kwargs)
                # 如果返回的是字典且包含code，则使用其结果码
                if isinstance(result, dict):
                    result_code = result.get("code", 0)
                    result_msg = result.get("msg", "成功")
                return result
            except Exception as e:
                result_code = 500
                result_msg = str(e)
                raise
            finally:
                duration = int((datetime.now() - start_time).total_seconds() * 1000)

                # 异步写入日志（需要在请求上下文中获取db session）
                # 这里只是记录时间，实际写入在中间件或依赖中完成

        return wrapper
    return decorator