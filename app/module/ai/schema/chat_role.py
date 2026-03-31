"""
AI 聊天角色相关 Schema
参考 ruoyi-vue-pro yudao-module-ai 模块的 AiChatRolePageReqVO、AiChatRoleRespVO
"""
from typing import Optional, List
from datetime import datetime
from pydantic import Field

from app.common.schema import CamelModel, CamelORMModel
from app.common.pagination import PageQuery


class ChatRolePageQuery(PageQuery):
    """AI 聊天角色分页查询"""

    name: Optional[str] = Field(None, description="角色名称")
    category: Optional[str] = Field(None, description="角色类别")
    public_status: Optional[bool] = Field(None, description="是否公开")


class ChatRoleCreate(CamelModel):
    """创建 AI 聊天角色请求"""

    user_id: Optional[int] = Field(None, description="用户编号")
    model_id: Optional[int] = Field(None, description="模型编号")
    name: str = Field(..., max_length=128, description="角色名称")
    avatar: str = Field(..., max_length=256, description="头像")
    category: Optional[str] = Field(None, max_length=32, description="角色类别")
    sort: Optional[int] = Field(0, description="角色排序")
    description: str = Field(..., max_length=256, description="角色描述")
    system_message: Optional[str] = Field(None, max_length=1024, description="角色上下文")
    knowledge_ids: Optional[str] = Field(None, max_length=256, description="关联的知识库编号数组")
    tool_ids: Optional[str] = Field(None, max_length=256, description="关联的工具编号数组")
    mcp_client_names: Optional[str] = Field(None, max_length=256, description="引用的 MCP Client 名字列表")
    public_status: Optional[int] = Field(0, description="是否公开: 0-否, 1-是")
    status: Optional[int] = Field(0, description="状态")


class ChatRoleUpdate(CamelModel):
    """更新 AI 聊天角色请求"""

    id: int = Field(..., description="角色编号")
    user_id: Optional[int] = Field(None, description="用户编号")
    model_id: Optional[int] = Field(None, description="模型编号")
    name: Optional[str] = Field(None, max_length=128, description="角色名称")
    avatar: Optional[str] = Field(None, max_length=256, description="头像")
    category: Optional[str] = Field(None, max_length=32, description="角色类别")
    sort: Optional[int] = Field(None, description="角色排序")
    description: Optional[str] = Field(None, max_length=256, description="角色描述")
    system_message: Optional[str] = Field(None, max_length=1024, description="角色上下文")
    knowledge_ids: Optional[str] = Field(None, max_length=256, description="关联的知识库编号数组")
    tool_ids: Optional[str] = Field(None, max_length=256, description="关联的工具编号数组")
    mcp_client_names: Optional[str] = Field(None, max_length=256, description="引用的 MCP Client 名字列表")
    public_status: Optional[int] = Field(None, description="是否公开: 0-否, 1-是")
    status: Optional[int] = Field(None, description="状态")


class ChatRoleResponse(CamelORMModel):
    """AI 聊天角色响应"""

    id: int = Field(..., description="角色编号")
    user_id: Optional[int] = Field(None, description="用户编号")
    model_id: Optional[int] = Field(None, description="模型编号")
    name: Optional[str] = Field(None, description="角色名称")
    avatar: Optional[str] = Field(None, description="头像")
    category: Optional[str] = Field(None, description="角色类别")
    sort: Optional[int] = Field(None, description="角色排序")
    description: Optional[str] = Field(None, description="角色描述")
    system_message: Optional[str] = Field(None, description="角色上下文")
    knowledge_ids: Optional[str] = Field(None, description="关联的知识库编号数组")
    tool_ids: Optional[str] = Field(None, description="关联的工具编号数组")
    mcp_client_names: Optional[str] = Field(None, description="引用的 MCP Client 名字列表")
    public_status: Optional[int] = Field(None, description="是否公开: 0-否, 1-是")
    status: Optional[int] = Field(None, description="状态")
    create_time: Optional[datetime] = Field(None, description="创建时间")