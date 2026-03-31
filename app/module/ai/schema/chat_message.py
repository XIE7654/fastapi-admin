"""
AI 聊天消息相关 Schema
参考 ruoyi-vue-pro yudao-module-ai AiChatMessageRespVO
"""
from typing import Optional, List
from datetime import datetime
from pydantic import Field

from app.common.schema import CamelModel, CamelORMModel
from app.common.pagination import PageQuery


class KnowledgeSegment(CamelModel):
    """知识库段落"""

    id: int = Field(..., description="段落编号")
    content: Optional[str] = Field(None, description="切片内容")
    document_id: Optional[int] = Field(None, description="文档编号")
    document_name: Optional[str] = Field(None, description="文档名称")


class ChatMessageResponse(CamelORMModel):
    """AI 聊天消息响应"""

    id: int = Field(..., description="编号")
    conversation_id: Optional[int] = Field(None, description="对话编号")
    reply_id: Optional[int] = Field(None, description="回复消息编号")
    type: Optional[str] = Field(None, description="消息类型")
    user_id: Optional[int] = Field(None, description="用户编号")
    role_id: Optional[int] = Field(None, description="角色编号")
    model: Optional[str] = Field(None, description="模型标识")
    model_id: Optional[int] = Field(None, description="模型编号")
    content: Optional[str] = Field(None, description="消息内容")
    reasoning_content: Optional[str] = Field(None, description="推理内容")
    use_context: Optional[bool] = Field(None, description="是否携带上下文")
    segment_ids: Optional[List[int]] = Field(None, description="知识库段落编号数组")
    segments: Optional[List[KnowledgeSegment]] = Field(None, description="知识库段落数组")
    web_search_pages: Optional[List[dict]] = Field(None, description="联网搜索的网页内容数组")
    attachment_urls: Optional[List[str]] = Field(None, description="附件 URL 数组")
    create_time: Optional[datetime] = Field(None, description="创建时间")

    # 仅在【对话管理】时加载
    role_name: Optional[str] = Field(None, description="角色名字")


class ChatMessagePageQuery(PageQuery):
    """AI 聊天消息分页查询"""

    conversation_id: Optional[int] = Field(None, description="对话编号")
    user_id: Optional[int] = Field(None, description="用户编号")
    content: Optional[str] = Field(None, description="消息内容")
    create_time: Optional[List[datetime]] = Field(None, description="创建时间范围")