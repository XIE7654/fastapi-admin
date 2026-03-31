"""
AI 聊天消息模型
参考 ruoyi-vue-pro yudao-module-ai AiChatMessageDO
"""
from sqlalchemy import Column, String, BigInteger, Integer, SmallInteger, Boolean, Text
from sqlalchemy.dialects.mysql import JSON

from app.module.system.model.base import Base, TimestampMixin, TenantMixin


class ChatMessage(Base, TimestampMixin, TenantMixin):
    """AI 聊天消息表"""

    __tablename__ = "ai_chat_message"

    conversation_id = Column(BigInteger, nullable=False, comment="对话编号")
    reply_id = Column(BigInteger, nullable=True, comment="回复消息编号")
    type = Column(String(32), nullable=False, comment="消息类型: user/assistant/system")
    user_id = Column(BigInteger, nullable=True, comment="用户编号")
    role_id = Column(BigInteger, nullable=True, comment="角色编号")
    model = Column(String(64), nullable=True, comment="模型标识")
    model_id = Column(BigInteger, nullable=True, comment="模型编号")
    content = Column(Text, nullable=False, comment="消息内容")
    reasoning_content = Column(Text, nullable=True, comment="推理内容")
    use_context = Column(Boolean, default=True, comment="是否携带上下文")
    segment_ids = Column(JSON, nullable=True, comment="知识库段落编号数组")
    web_search_pages = Column(JSON, nullable=True, comment="联网搜索的网页内容数组")
    attachment_urls = Column(JSON, nullable=True, comment="附件 URL 数组")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, type={self.type})>"