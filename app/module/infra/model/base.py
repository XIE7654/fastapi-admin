"""
模型基类
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, DateTime, BigInteger
from sqlalchemy.orm import declared_attr

from app.core.database import Base as _Base


class Base(_Base):
    """模型基类"""

    __abstract__ = True

    # 主键
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")

    @declared_attr
    def __tablename__(cls):
        """自动生成表名"""
        import re
        name = re.sub(r'([A-Z])', r'_\1', cls.__name__).lower()
        return name.lstrip('_')


class TimestampMixin:
    """时间戳混入类"""

    @declared_attr
    def creator(cls):
        return Column(String(64), nullable=True, default="", comment="创建者")

    @declared_attr
    def create_time(cls):
        return Column(DateTime, default=datetime.now, comment="创建时间")

    @declared_attr
    def updater(cls):
        return Column(String(64), nullable=True, default="", comment="更新者")

    @declared_attr
    def update_time(cls):
        return Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class TenantMixin:
    """多租户混入类"""

    @declared_attr
    def deleted(cls):
        return Column(Integer, default=0, comment="是否删除: 0-未删除, 1-已删除")

    @declared_attr
    def tenant_id(cls):
        return Column(BigInteger, default=0, index=True, comment="租户编号")


# 导入 String
from sqlalchemy import String