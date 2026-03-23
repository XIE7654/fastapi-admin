"""
字典数据模型
"""
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, BigInteger, SmallInteger, ForeignKey

from app.module.system.model.base import Base, TimestampMixin, SoftDeleteMixin


class DictData(Base, TimestampMixin, SoftDeleteMixin):
    """字典数据表"""

    __tablename__ = "system_dict_data"

    sort = Column(Integer, default=0, comment="显示顺序")
    label = Column(String(100), nullable=False, comment="字典标签")
    value = Column(String(100), nullable=False, comment="字典键值")
    dict_type = Column(String(100), nullable=False, index=True, comment="字典类型")
    status = Column(SmallInteger, default=0, comment="状态: 0-正常, 1-禁用")
    color_type = Column(String(100), nullable=True, comment="颜色类型: default/primary/success/info/warning/danger")
    css_class = Column(String(100), nullable=True, comment="CSS类名")
    remark = Column(String(500), nullable=True, comment="备注")

    def __repr__(self):
        return f"<DictData(id={self.id}, label={self.label}, value={self.value})>"

    @property
    def is_active(self) -> bool:
        """是否激活"""
        return self.status == 0