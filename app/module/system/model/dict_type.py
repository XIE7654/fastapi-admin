"""
字典类型模型
"""
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, BigInteger, SmallInteger

from app.module.system.model.base import Base, TimestampMixin, TenantMixin


class DictType(Base, TimestampMixin):
    """字典类型表"""

    __tablename__ = "system_dict_type"

    name = Column(String(100), nullable=False, comment="字典名称")
    type = Column(String(100), unique=True, nullable=False, comment="字典类型")
    status = Column(SmallInteger, default=0, comment="状态: 0-正常, 1-禁用")
    remark = Column(String(500), nullable=True, comment="备注")

    def __repr__(self):
        return f"<DictType(id={self.id}, name={self.name}, type={self.type})>"

    @property
    def is_active(self) -> bool:
        """是否激活"""
        return self.status == 0