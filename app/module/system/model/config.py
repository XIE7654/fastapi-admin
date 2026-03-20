"""
参数配置模型
"""
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, BigInteger, SmallInteger

from app.module.system.model.base import Base, TimestampMixin, TenantMixin


class Config(Base, TimestampMixin, TenantMixin):
    """参数配置表"""

    __tablename__ = "infra_config"

    category = Column(String(50), nullable=False, comment="参数分类")
    name = Column(String(100), nullable=False, comment="参数名称")
    config_key = Column(String(100), unique=True, nullable=False, comment="参数键名")
    value = Column(String(500), nullable=False, comment="参数键值")
    type = Column(SmallInteger, default=1, comment="参数类型: 1-系统, 2-自定义")
    visible = Column(SmallInteger, default=0, comment="是否可见: 0-是, 1-否")
    remark = Column(String(500), nullable=True, comment="备注")

    def __repr__(self):
        return f"<Config(id={self.id}, config_key={self.config_key}, value={self.value})>"