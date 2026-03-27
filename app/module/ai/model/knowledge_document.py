"""
AI 知识库文档模型
"""
from sqlalchemy import Column, String, BigInteger, SmallInteger, Integer, Text

from app.module.system.model.base import Base, TimestampMixin, TenantMixin


class KnowledgeDocument(Base, TimestampMixin, TenantMixin):
    """AI 知识库文档表"""

    __tablename__ = "ai_knowledge_document"

    knowledge_id = Column(BigInteger, nullable=False, comment="知识库编号")
    name = Column(String(255), nullable=False, comment="文档名称")
    url = Column(String(1024), nullable=False, comment="文件 URL")
    content = Column(Text, nullable=False, comment="内容")
    word_count = Column(Integer, nullable=True, comment="字数")
    slice_status = Column(SmallInteger, nullable=False, comment="分片状态")
    slice_num = Column(Integer, nullable=True, comment="分片数量")
    character_count = Column(Integer, nullable=True, comment="字符数")

    def __repr__(self):
        return f"<KnowledgeDocument(id={self.id}, name={self.name})>"