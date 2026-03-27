"""
AI 工具模型
"""
from sqlalchemy import Column, String, SmallInteger

from app.module.system.model.base import Base, TimestampMixin, TenantMixin


class Tool(Base, TimestampMixin, TenantMixin):
    """AI 工具表"""

    __tablename__ = "ai_tool"

    name = Column(String(128), nullable=False, comment="工具名称")
    description = Column(String(256), nullable=True, comment="工具描述")
    status = Column(SmallInteger, nullable=False, comment="状态")

    def __repr__(self):
        return f"<Tool(id={self.id}, name={self.name})>"