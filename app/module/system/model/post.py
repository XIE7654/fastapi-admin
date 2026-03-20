"""
岗位模型
"""
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, BigInteger, SmallInteger

from app.module.system.model.base import Base, TimestampMixin, TenantMixin


class Post(Base, TimestampMixin, TenantMixin):
    """岗位表"""

    __tablename__ = "system_post"

    name = Column(String(50), nullable=False, comment="岗位名称")
    code = Column(String(64), unique=True, nullable=False, comment="岗位编码")
    sort = Column(Integer, default=0, comment="显示顺序")
    status = Column(SmallInteger, default=0, comment="状态: 0-正常, 1-禁用")
    remark = Column(String(500), nullable=True, comment="备注")

    def __repr__(self):
        return f"<Post(id={self.id}, name={self.name}, code={self.code})>"

    @property
    def is_active(self) -> bool:
        """是否激活"""
        return self.status == 0