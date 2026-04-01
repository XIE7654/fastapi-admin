"""
AI 聊天对话相关 Schema
参考 ruoyi-vue-pro yudao-module-ai AiChatConversationPageReqVO、AiChatConversationRespVO
"""
from typing import Optional, List, Any
from datetime import datetime
from pydantic import Field, field_validator

from app.common.schema import CamelModel, CamelORMModel
from app.common.pagination import PageQuery


def convert_bit_to_int(v: Any) -> Optional[int]:
    """将 MySQL BIT 类型转换为整数"""
    if v is None:
        return None
    if isinstance(v, bytes):
        return int.from_bytes(v, byteorder='big')
    if isinstance(v, bool):
        return 1 if v else 0
    return int(v)


class ChatConversationPageQuery(PageQuery):
    """AI 聊天对话分页查询"""

    user_id: Optional[int] = Field(None, description="用户编号")
    title: Optional[str] = Field(None, description="对话标题")


class ChatConversationCreate(CamelModel):
    """创建 AI 聊天对话请求"""

    user_id: int = Field(..., description="用户编号")
    role_id: Optional[int] = Field(None, description="聊天角色")
    title: str = Field(..., max_length=256, description="对话标题")
    model_id: int = Field(..., description="模型编号")
    model: str = Field(..., max_length=64, description="模型标识")
    system_message: Optional[str] = Field(None, max_length=1024, description="角色设定")
    temperature: float = Field(0.8, description="温度参数")
    max_tokens: int = Field(4096, description="单条回复的最大 Token 数量")
    max_contexts: int = Field(10, description="上下文的最大 Message 数量")


class ChatConversationUpdate(CamelModel):
    """更新 AI 聊天对话请求"""

    id: int = Field(..., description="对话编号")
    title: Optional[str] = Field(None, max_length=256, description="对话标题")
    pinned: Optional[int] = Field(None, description="是否置顶: 0-否, 1-是")
    system_message: Optional[str] = Field(None, max_length=1024, description="角色设定")
    temperature: Optional[float] = Field(None, description="温度参数")
    max_tokens: Optional[int] = Field(None, description="单条回复的最大 Token 数量")
    max_contexts: Optional[int] = Field(None, description="上下文的最大 Message 数量")


class ChatConversationResponse(CamelORMModel):
    """AI 聊天对话响应"""

    id: int = Field(..., description="对话编号")
    user_id: Optional[int] = Field(None, description="用户编号")
    title: Optional[str] = Field(None, description="对话标题")
    pinned: Optional[int] = Field(None, description="是否置顶: 0-否, 1-是")
    pinned_time: Optional[datetime] = Field(None, description="置顶时间")
    role_id: Optional[int] = Field(None, description="角色编号")
    model_id: Optional[int] = Field(None, description="模型编号")
    model: Optional[str] = Field(None, description="模型标识")
    system_message: Optional[str] = Field(None, description="角色设定")
    temperature: Optional[float] = Field(None, description="温度参数")
    max_tokens: Optional[int] = Field(None, description="单条回复的最大 Token 数量")
    max_contexts: Optional[int] = Field(None, description="上下文的最大 Message 数量")
    create_time: Optional[datetime] = Field(None, description="创建时间")

    # 关联信息
    role_name: Optional[str] = Field(None, description="角色名称")
    role_avatar: Optional[str] = Field(None, description="角色头像")
    model_name: Optional[str] = Field(None, description="模型名称")

    # 消息数量
    message_count: Optional[int] = Field(None, description="消息数量")

    @field_validator('pinned', mode='before')
    @classmethod
    def validate_bit_field(cls, v: Any) -> Optional[int]:
        """处理 MySQL BIT 类型字段"""
        return convert_bit_to_int(v)