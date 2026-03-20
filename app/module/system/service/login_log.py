"""
登录日志服务
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.system.model.login_log import LoginLog
from app.module.system.schema.log import LoginLogPageQuery


def parse_user_agent(user_agent: str) -> tuple:
    """
    解析User-Agent字符串

    Returns:
        (browser, os) 浏览器和操作系统信息
    """
    if not user_agent:
        return None, None

    browser = None
    os_info = None

    # 简单的User-Agent解析
    ua_lower = user_agent.lower()

    # 浏览器检测
    if "edg/" in ua_lower:
        browser = "Edge"
    elif "chrome/" in ua_lower:
        browser = "Chrome"
    elif "firefox/" in ua_lower:
        browser = "Firefox"
    elif "safari/" in ua_lower and "chrome" not in ua_lower:
        browser = "Safari"
    elif "opera/" in ua_lower or "opr/" in ua_lower:
        browser = "Opera"
    elif "msie" in ua_lower or "trident/" in ua_lower:
        browser = "IE"

    # 操作系统检测
    if "windows" in ua_lower:
        os_info = "Windows"
    elif "mac os" in ua_lower:
        os_info = "MacOS"
    elif "linux" in ua_lower:
        os_info = "Linux"
    elif "android" in ua_lower:
        os_info = "Android"
    elif "iphone" in ua_lower or "ipad" in ua_lower:
        os_info = "iOS"

    return browser, os_info


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
        result_code: int = 0,
        result_msg: str = "成功",
        tenant_id: int = None,
    ) -> LoginLog:
        """创建登录日志"""
        # 解析User-Agent
        browser, os_info = parse_user_agent(user_agent)

        log = LoginLog(
            log_type=log_type,
            user_id=user_id,
            username=username,
            user_ip=user_ip,
            user_agent=user_agent,
            browser=browser,
            os=os_info,
            result_code=result_code,
            result_msg=result_msg,
            login_time=datetime.now(),
            tenant_id=tenant_id or 1,
        )
        db.add(log)
        await db.flush()
        return log

    @staticmethod
    async def get_list(db: AsyncSession, query: LoginLogPageQuery) -> tuple[List[LoginLog], int]:
        """分页查询登录日志"""
        conditions = [LoginLog.deleted == 0]

        if query.user_id:
            conditions.append(LoginLog.user_id == query.user_id)
        if query.username:
            conditions.append(LoginLog.username.like(f"%{query.username}%"))
        if query.log_type:
            conditions.append(LoginLog.log_type == query.log_type)
        if query.result_code is not None:
            conditions.append(LoginLog.result_code == query.result_code)
        if query.user_ip:
            conditions.append(LoginLog.user_ip.like(f"%{query.user_ip}%"))
        if query.login_time and len(query.login_time) == 2:
            conditions.append(LoginLog.login_time.between(query.login_time[0], query.login_time[1]))

        # 查询总数
        count_result = await db.execute(
            select(LoginLog).where(and_(*conditions))
        )
        total = len(count_result.all())

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
        result_code: int = 0,
        result_msg: str = "登录成功",
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
            result_code=result_code,
            result_msg=result_msg,
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
            result_code=0,
            result_msg="登出成功",
            tenant_id=tenant_id,
        )