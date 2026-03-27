"""
AI 知识库模型
"""
from sqlalchemy import Column, String, BigInteger, SmallInteger, Float, Integer, Text

from app.module.system.model.base import Base, TimestampMixin, TenantMixin


class Knowledge(Base, TimestampMixin, TenantMixin):
    """AI 知识库表"""

    __tablename__ = "ai_knowledge"

    name = Column(String(255), nullable=False, comment="知识库名称")
    description = Column(Text, nullable=True, comment="知识库描述")
    embedding_model_id = Column(BigInteger, nullable=False, comment="向量模型编号")
    embedding_model = Column(String(32), nullable=False, comment="向量模型标识")
    top_k = Column(Integer, nullable=False, comment="topK")
    similarity_threshold = Column(Float, nullable=False, comment="相似度阈值")
    status = Column(SmallInteger, nullable=False, comment="是否启用")

    def __repr__(self):
        return f"<Knowledge(id={self.id}, name={self.name})>"