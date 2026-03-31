"""
AI API 密钥相关 Schema
参考 ruoyi-vue-pro yudao-module-ai 模块的 AiApiKeyPageReqVO、AiApiKeySaveReqVO、AiApiKeyRespVO
"""
from typing import Optional
from datetime import datetime
from pydantic import Field

from app.common.schema import CamelModel, CamelORMModel
from app.common.pagination import PageQuery


class ApiKeyBase(CamelModel):
    """API 密钥基础信息"""

    name: str = Field(..., max_length=255, description="名称")
    api_key: str = Field(..., max_length=1024, description="密钥")
    platform: str = Field(..., max_length=255, description="平台")
    url: Optional[str] = Field(None, max_length=255, description="自定义 API 地址")
    status: int = Field(..., description="状态")


class ApiKeyCreate(ApiKeyBase):
    """创建 API 密钥请求"""

    pass


class ApiKeyUpdate(CamelModel):
    """更新 API 密钥请求"""

    id: int = Field(..., description="编号")
    name: Optional[str] = Field(None, max_length=255, description="名称")
    api_key: Optional[str] = Field(None, max_length=1024, description="密钥")
    platform: Optional[str] = Field(None, max_length=255, description="平台")
    url: Optional[str] = Field(None, max_length=255, description="自定义 API 地址")
    status: Optional[int] = Field(None, description="状态")


class ApiKeyResponse(CamelORMModel):
    """API 密钥响应"""

    id: int = Field(..., description="编号")
    name: Optional[str] = Field(None, description="名称")
    api_key: Optional[str] = Field(None, description="密钥")
    platform: Optional[str] = Field(None, description="平台")
    url: Optional[str] = Field(None, description="自定义 API 地址")
    status: Optional[int] = Field(None, description="状态")
    create_time: Optional[datetime] = Field(None, description="创建时间")


class ApiKeySimpleResponse(CamelORMModel):
    """API 密钥简要响应"""

    id: int = Field(..., description="编号")
    name: Optional[str] = Field(None, description="名称")


class ApiKeyPageQuery(PageQuery):
    """API 密钥分页查询"""

    name: Optional[str] = Field(None, description="名称")
    platform: Optional[str] = Field(None, description="平台")
    status: Optional[int] = Field(None, description="状态")