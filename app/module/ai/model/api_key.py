"""
AI API 密钥模型
"""
from sqlalchemy import Column, String, Integer, SmallInteger

from app.module.system.model.base import Base, TimestampMixin, TenantMixin


class ApiKey(Base, TimestampMixin, TenantMixin):
    """AI API 密钥表"""

    __tablename__ = "ai_api_key"

    name = Column(String(255), nullable=False, comment="名称")
    api_key = Column(String(1024), nullable=False, comment="密钥")
    platform = Column(String(255), nullable=False, comment="平台")
    url = Column(String(255), nullable=True, comment="自定义 API 地址")
    status = Column(Integer, nullable=False, comment="状态")

    def __repr__(self):
        return f"<ApiKey(id={self.id}, name={self.name}, platform={self.platform})>"