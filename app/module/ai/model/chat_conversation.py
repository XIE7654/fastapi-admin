"""
AI 聊天对话模型
"""
from sqlalchemy import Column, String, BigInteger, Integer, SmallInteger, DateTime, Float

from app.module.system.model.base import Base, TimestampMixin, TenantMixin


class ChatConversation(Base, TimestampMixin, TenantMixin):
    """AI 聊天对话表"""

    __tablename__ = "ai_chat_conversation"

    user_id = Column(BigInteger, nullable=False, comment="用户编号")
    role_id = Column(BigInteger, nullable=True, comment="聊天角色")
    title = Column(String(256), nullable=False, comment="对话标题")
    model_id = Column(BigInteger, nullable=False, comment="模型编号")
    model = Column(String(64), nullable=False, comment="模型标识")
    pinned = Column(SmallInteger, default=0, comment="是否置顶: 0-否, 1-是")
    pinned_time = Column(DateTime, nullable=True, comment="置顶时间")
    system_message = Column(String(1024), nullable=True, comment="角色设定")
    temperature = Column(Float, nullable=False, comment="温度参数")
    max_tokens = Column(Integer, nullable=False, comment="单条回复的最大 Token 数量")
    max_contexts = Column(Integer, nullable=False, comment="上下文的最大 Message 数量")

    def __repr__(self):
        return f"<ChatConversation(id={self.id}, title={self.title})>"