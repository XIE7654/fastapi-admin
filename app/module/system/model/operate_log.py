"""
操作日志模型 (V2版本)
"""
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, BigInteger, SmallInteger, Text, Boolean

from app.module.system.model.base import Base, TenantMixin


class OperateLog(Base, TenantMixin):
    """操作日志表 V2版本"""

    __tablename__ = "system_operate_log"

    # 链路追踪
    trace_id = Column(String(64), nullable=True, default="", comment="链路追踪编号")

    # 用户信息
    user_id = Column(BigInteger, nullable=False, comment="用户编号")
    user_type = Column(SmallInteger, default=0, comment="用户类型")

    # 操作信息
    type = Column(String(50), nullable=False, comment="操作模块类型")
    sub_type = Column(String(50), nullable=False, comment="操作名")
    biz_id = Column(BigInteger, nullable=False, comment="操作数据模块编号")
    action = Column(String(2000), nullable=True, default="", comment="操作内容")
    success = Column(Boolean, default=True, comment="操作结果")
    extra = Column(String(2000), nullable=True, default="", comment="拓展字段")

    # 请求信息
    request_method = Column(String(16), nullable=True, default="", comment="请求方法名")
    request_url = Column(String(255), nullable=True, default="", comment="请求地址")
    user_ip = Column(String(50), nullable=True, comment="用户IP")
    user_agent = Column(String(512), nullable=True, comment="浏览器UA")