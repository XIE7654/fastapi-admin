"""
AI 写作模型
"""
from sqlalchemy import Column, String, BigInteger, SmallInteger, Integer

from app.module.system.model.base import Base, TimestampMixin, TenantMixin


class Write(Base, TimestampMixin, TenantMixin):
    """AI 写作表"""

    __tablename__ = "ai_write"

    user_id = Column(BigInteger, nullable=False, comment="用户编号")
    type = Column(Integer, nullable=True, comment="写作类型")
    platform = Column(String(255), nullable=False, comment="平台")
    model_id = Column(BigInteger, nullable=False, comment="模型编号")
    model = Column(String(255), nullable=False, comment="模型")
    prompt = Column(String(512), nullable=False, comment="生成内容提示")
    generated_content = Column(String(5120), nullable=True, comment="生成的内容")
    original_content = Column(String(5120), nullable=True, comment="原文")
    length = Column(SmallInteger, nullable=True, comment="长度提示词")
    format = Column(SmallInteger, nullable=True, comment="格式提示词")
    tone = Column(SmallInteger, nullable=True, comment="语气提示词")
    language = Column(SmallInteger, nullable=True, comment="语言提示词")
    error_message = Column(String(255), nullable=True, comment="错误信息")

    def __repr__(self):
        return f"<Write(id={self.id}, prompt={self.prompt[:20]}...)>"