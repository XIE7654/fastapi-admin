"""
AI 工作流模型
"""
from sqlalchemy import Column, String, SmallInteger, Text

from app.module.system.model.base import Base, TimestampMixin, TenantMixin


class Workflow(Base, TimestampMixin, TenantMixin):
    """AI 工作流表"""

    __tablename__ = "ai_workflow"

    name = Column(String(255), nullable=False, comment="流程名称")
    code = Column(String(255), nullable=False, comment="流程标识")
    graph = Column(Text, nullable=False, comment="流程模型")
    status = Column(SmallInteger, nullable=False, comment="状态")
    remark = Column(String(256), nullable=True, comment="备注")

    def __repr__(self):
        return f"<Workflow(id={self.id}, name={self.name})>"