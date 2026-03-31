"""
AI 工具相关 Schema
参考 ruoyi-vue-pro yudao-module-ai 模块的 AiToolPageReqVO、AiToolSaveReqVO、AiToolRespVO
"""
from typing import Optional, List
from datetime import datetime
from pydantic import Field

from app.common.schema import CamelModel, CamelORMModel
from app.common.pagination import PageQuery


class AiToolBase(CamelModel):
    """AI 工具基础信息"""

    name: str = Field(..., max_length=128, description="工具名称")
    description: Optional[str] = Field(None, max_length=256, description="工具描述")
    status: int = Field(..., ge=0, le=1, description="状态: 0-开启, 1-禁用")


class AiToolCreate(AiToolBase):
    """创建 AI 工具请求"""

    pass


class AiToolUpdate(CamelModel):
    """更新 AI 工具请求"""

    id: int = Field(..., description="工具编号")
    name: Optional[str] = Field(None, max_length=128, description="工具名称")
    description: Optional[str] = Field(None, max_length=256, description="工具描述")
    status: Optional[int] = Field(None, ge=0, le=1, description="状态")


class AiToolResponse(CamelORMModel):
    """AI 工具响应"""

    id: int = Field(..., description="编号")
    name: Optional[str] = Field(None, description="工具名称")
    description: Optional[str] = Field(None, description="工具描述")
    status: Optional[int] = Field(None, description="状态")
    create_time: Optional[datetime] = Field(None, description="创建时间")


class AiToolSimpleResponse(CamelORMModel):
    """AI 工具简要响应（用于前端下拉选项）"""

    id: int = Field(..., description="编号")
    name: Optional[str] = Field(None, description="工具名称")


class AiToolPageQuery(PageQuery):
    """AI 工具分页查询"""

    name: Optional[str] = Field(None, description="工具名称")
    description: Optional[str] = Field(None, description="工具描述")
    status: Optional[int] = Field(None, ge=0, le=1, description="状态")