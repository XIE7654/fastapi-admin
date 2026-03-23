"""
登录日志模型
"""
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, BigInteger, SmallInteger

from app.module.system.model.base import Base, TenantMixin


class LoginLog(Base, TenantMixin):
    """登录日志表"""

    __tablename__ = "system_login_log"

    # 日志信息
    log_type = Column(SmallInteger, default=100, comment="日志类型: 100-登录, 101-登出")
    trace_id = Column(String(64), nullable=True, comment="链路追踪编号")

    # 用户信息
    user_id = Column(BigInteger, nullable=True, comment="用户ID")
    username = Column(String(50), nullable=True, comment="用户账号")
    user_type = Column(SmallInteger, default=2, comment="用户类型: 1-管理员, 2-普通用户")

    # 登录结果
    result = Column(Integer, default=0, comment="结果码")

    # 客户端信息
    user_ip = Column(String(50), nullable=True, comment="用户IP")
    user_agent = Column(String(512), nullable=True, comment="浏览器UA")

    # 时间
    login_time = Column(DateTime, default=datetime.now, comment="登录时间")