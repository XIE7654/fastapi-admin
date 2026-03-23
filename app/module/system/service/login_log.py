"""
登录日志服务
"""
from typing import Optional, List, Tuple
from datetime import datetime
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.system.model.login_log import LoginLog
from app.module.system.schema.log import LoginLogPageQuery


class LoginLogService:
    """登录日志服务"""

    # 日志类型
    LOG_TYPE_LOGIN = 100
    LOG_TYPE_LOGOUT = 101

    @staticmethod
    async def create(
        db: AsyncSession,
        log_type: int,
        user_id: int,
        username: str,
        user_ip: str,
        user_agent: str,
        result: int = 0,
        tenant_id: int = None,
    ) -> LoginLog:
        """创建登录日志"""
        log = LoginLog(
            log_type=log_type,
            user_id=user_id,
            username=username,
            user_ip=user_ip,
            user_agent=user_agent,
            result=result,
            tenant_id=tenant_id or 1,
        )
        db.add(log)
        await db.flush()
        return log

    @staticmethod
    async def get_list(db: AsyncSession, query: LoginLogPageQuery) -> Tuple[List[LoginLog], int]:
        """分页查询登录日志"""
        conditions = [LoginLog.deleted == 0]

        if query.user_id:
            conditions.append(LoginLog.user_id == query.user_id)
        if query.username:
            conditions.append(LoginLog.username.like(f"%{query.username}%"))
        if query.log_type:
            conditions.append(LoginLog.log_type == query.log_type)
        if query.result is not None:
            conditions.append(LoginLog.result == query.result)
        if query.user_ip:
            conditions.append(LoginLog.user_ip.like(f"%{query.user_ip}%"))
        if query.create_time and len(query.create_time) == 2:
            conditions.append(LoginLog.create_time.between(query.create_time[0], query.create_time[1]))

        # 查询总数
        count_query = select(func.count()).select_from(LoginLog).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        result = await db.execute(
            select(LoginLog)
            .where(and_(*conditions))
            .order_by(LoginLog.id.desc())
            .offset(query.offset)
            .limit(query.limit)
        )
        logs = result.scalars().all()

        return list(logs), total

    @staticmethod
    async def create_login_log(
        db: AsyncSession,
        user_id: int,
        username: str,
        user_ip: str,
        user_agent: str,
        result: int = 0,
        tenant_id: int = None,
    ) -> LoginLog:
        """创建登录日志"""
        return await LoginLogService.create(
            db=db,
            log_type=LoginLogService.LOG_TYPE_LOGIN,
            user_id=user_id,
            username=username,
            user_ip=user_ip,
            user_agent=user_agent,
            result=result,
            tenant_id=tenant_id,
        )

    @staticmethod
    async def create_logout_log(
        db: AsyncSession,
        user_id: int,
        username: str,
        user_ip: str,
        user_agent: str,
        tenant_id: int = None,
    ) -> LoginLog:
        """创建登出日志"""
        return await LoginLogService.create(
            db=db,
            log_type=LoginLogService.LOG_TYPE_LOGOUT,
            user_id=user_id,
            username=username,
            user_ip=user_ip,
            user_agent=user_agent,
            result=0,
            tenant_id=tenant_id,
        )