"""
AI 聊天消息模型
"""
from sqlalchemy import Column, String, BigInteger, SmallInteger

from app.module.system.model.base import Base, TimestampMixin, TenantMixin


class ChatMessage(Base, TimestampMixin, TenantMixin):
    """AI 聊天消息表"""

    __tablename__ = "ai_chat_message"

    conversation_id = Column(BigInteger, nullable=False, comment="对话编号")
    role = Column(String(32), nullable=False, comment="角色")
    content = Column(String(16384), nullable=False, comment="消息内容")
    receive_tokens = Column(Integer, nullable=True, comment="接收 Tokens")
    generate_tokens = Column(Integer, nullable=True, comment="生成 Tokens")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role={self.role})>"