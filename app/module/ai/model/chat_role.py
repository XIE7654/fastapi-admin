"""
AI 聊天角色模型
"""
from sqlalchemy import Column, String, BigInteger, Integer, SmallInteger

from app.module.system.model.base import Base, TimestampMixin, TenantMixin


class ChatRole(Base, TimestampMixin, TenantMixin):
    """AI 聊天角色表"""

    __tablename__ = "ai_chat_role"

    user_id = Column(BigInteger, nullable=True, comment="用户编号")
    model_id = Column(BigInteger, nullable=True, comment="模型编号")
    name = Column(String(128), nullable=False, comment="角色名称")
    avatar = Column(String(256), nullable=False, comment="头像")
    category = Column(String(32), nullable=True, comment="角色类别")
    sort = Column(Integer, default=0, comment="角色排序")
    description = Column(String(256), nullable=False, comment="角色描述")
    system_message = Column(String(1024), nullable=True, comment="角色上下文")
    knowledge_ids = Column(String(256), nullable=True, comment="关联的知识库编号数组")
    tool_ids = Column(String(256), nullable=True, comment="关联的工具编号数组")
    mcp_client_names = Column(String(256), nullable=True, comment="引用的 MCP Client 名字列表")
    public_status = Column(SmallInteger, default=0, comment="是否公开: 0-否, 1-是")
    status = Column(SmallInteger, default=0, comment="状态")

    def __repr__(self):
        return f"<ChatRole(id={self.id}, name={self.name})>"