"""
AI 知识库分段模型
"""
from sqlalchemy import Column, String, BigInteger, Integer, Text

from app.module.system.model.base import Base, TimestampMixin, TenantMixin


class KnowledgeSegment(Base, TimestampMixin, TenantMixin):
    """AI 知识库分段表"""

    __tablename__ = "ai_knowledge_segment"

    knowledge_id = Column(BigInteger, nullable=False, comment="知识库编号")
    document_id = Column(BigInteger, nullable=False, comment="文档编号")
    content = Column(Text, nullable=False, comment="内容")
    word_count = Column(Integer, nullable=True, comment="字数")
    tokens = Column(Integer, nullable=True, comment="tokens 数量")

    def __repr__(self):
        return f"<KnowledgeSegment(id={self.id}, knowledge_id={self.knowledge_id})>"