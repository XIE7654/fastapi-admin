"""
AI 思维导图相关 Schema
参考 ruoyi-vue-pro yudao-module-ai AiMindMapRespVO
"""
from typing import Optional, List
from datetime import datetime
from pydantic import Field

from app.common.schema import CamelModel, CamelORMModel
from app.common.pagination import PageQuery


class MindMapResponse(CamelORMModel):
    """AI 思维导图响应"""

    id: int = Field(..., description="编号")
    user_id: Optional[int] = Field(None, description="用户编号")
    prompt: Optional[str] = Field(None, description="生成内容提示")
    generated_content: Optional[str] = Field(None, description="生成的思维导图内容")
    platform: Optional[str] = Field(None, description="平台")
    model: Optional[str] = Field(None, description="模型")
    error_message: Optional[str] = Field(None, description="错误信息")
    create_time: Optional[datetime] = Field(None, description="创建时间")


class MindMapPageQuery(PageQuery):
    """AI 思维导图分页查询"""

    user_id: Optional[int] = Field(None, description="用户编号")
    prompt: Optional[str] = Field(None, description="生成内容提示")
    create_time: Optional[List[datetime]] = Field(None, description="创建时间范围")