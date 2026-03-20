"""
通知公告模型
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, BigInteger, SmallInteger, Text

from app.module.system.model.base import Base, TimestampMixin, TenantMixin


class Notice(Base, TimestampMixin, TenantMixin):
    """通知公告表"""

    __tablename__ = "system_notice"

    title = Column(String(50), nullable=False, comment="公告标题")
    content = Column(Text, nullable=False, comment="公告内容")
    type = Column(SmallInteger, nullable=False, comment="公告类型: 1-通知, 2-公告")
    status = Column(SmallInteger, default=0, comment="公告状态: 0-正常, 1-关闭")