"""
AI 思维导图模型
"""
from sqlalchemy import Column, String, BigInteger, Text

from app.module.system.model.base import Base, TimestampMixin, TenantMixin


class MindMap(Base, TimestampMixin, TenantMixin):
    """AI 思维导图表"""

    __tablename__ = "ai_mind_map"

    user_id = Column(BigInteger, nullable=False, comment="用户编号")
    prompt = Column(Text, nullable=False, comment="生成内容提示")
    generated_content = Column(Text, nullable=True, comment="生成的思维导图内容")
    platform = Column(String(64), nullable=False, comment="平台")
    model_id = Column(BigInteger, nullable=False, comment="模型编号")
    model = Column(String(50), nullable=False, comment="模型")
    error_message = Column(String(1024), nullable=True, comment="错误信息")

    def __repr__(self):
        return f"<MindMap(id={self.id}, prompt={self.prompt[:20]}...)>"