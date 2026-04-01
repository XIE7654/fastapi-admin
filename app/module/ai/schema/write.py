"""
AI 写作相关 Schema
参考 ruoyi-vue-pro yudao-module-ai 模块的 AiWritePageReqVO、AiWriteRespVO、AiWriteGenerateReqVO
"""
from typing import Optional
from datetime import datetime
from pydantic import Field

from app.common.schema import CamelModel, CamelORMModel
from app.common.pagination import PageQuery


class WritePageQuery(PageQuery):
    """AI 写作分页查询"""

    user_id: Optional[int] = Field(None, description="用户编号")
    type: Optional[int] = Field(None, description="写作类型")
    platform: Optional[str] = Field(None, description="平台")


class WriteGenerateReqVO(CamelModel):
    """AI 写作生成请求"""

    type: int = Field(..., description="写作类型")
    prompt: Optional[str] = Field(None, description="写作内容提示")
    original_content: Optional[str] = Field(None, description="原文")
    length: int = Field(..., description="长度")
    format: int = Field(..., description="格式")
    tone: int = Field(..., description="语气")
    language: int = Field(..., description="语言")


class WriteResponse(CamelORMModel):
    """AI 写作响应"""

    id: int = Field(..., description="编号")
    user_id: Optional[int] = Field(None, description="用户编号")
    type: Optional[int] = Field(None, description="写作类型")
    platform: Optional[str] = Field(None, description="平台")
    model_id: Optional[int] = Field(None, description="模型编号")
    model: Optional[str] = Field(None, description="模型")
    prompt: Optional[str] = Field(None, description="生成内容提示")
    generated_content: Optional[str] = Field(None, description="生成的内容")
    original_content: Optional[str] = Field(None, description="原文")
    length: Optional[int] = Field(None, description="长度提示词")
    format: Optional[int] = Field(None, description="格式提示词")
    tone: Optional[int] = Field(None, description="语气提示词")
    language: Optional[int] = Field(None, description="语言提示词")
    error_message: Optional[str] = Field(None, description="错误信息")
    create_time: Optional[datetime] = Field(None, description="创建时间")