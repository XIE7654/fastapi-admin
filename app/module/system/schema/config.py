"""
参数配置Schema
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from app.common.pagination import PageQuery


class ConfigBase(BaseModel):
    """参数配置基础信息"""

    category: Optional[str] = Field(None, max_length=50, description="参数分类")
    name: Optional[str] = Field(None, max_length=100, description="参数名称")
    key: Optional[str] = Field(None, max_length=100, description="参数键名")
    value: Optional[str] = Field(None, max_length=500, description="参数键值")
    type: Optional[int] = Field(default=1, ge=1, le=2, description="参数类型: 1-系统, 2-自定义")
    visible: Optional[int] = Field(default=0, ge=0, le=1, description="是否可见: 0-是, 1-否")
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class ConfigCreate(ConfigBase):
    """创建参数配置请求"""

    category: str = Field(..., max_length=50, description="参数分类")
    name: str = Field(..., max_length=100, description="参数名称")
    key: str = Field(..., max_length=100, description="参数键名")
    value: str = Field(..., max_length=500, description="参数键值")

    @field_validator("key")
    @classmethod
    def validate_key(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("参数键名不能为空")
        return v.strip()


class ConfigUpdate(BaseModel):
    """更新参数配置请求"""

    category: Optional[str] = Field(None, max_length=50, description="参数分类")
    name: Optional[str] = Field(None, max_length=100, description="参数名称")
    value: Optional[str] = Field(None, max_length=500, description="参数键值")
    visible: Optional[int] = Field(None, ge=0, le=1, description="是否可见")
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class ConfigResponse(ConfigBase):
    """参数配置响应"""

    id: int = Field(..., description="参数ID")
    create_time: Optional[datetime] = Field(None, description="创建时间")

    model_config = {"from_attributes": True}


class ConfigPageQuery(PageQuery):
    """参数配置分页查询"""

    category: Optional[str] = Field(None, description="参数分类")
    name: Optional[str] = Field(None, description="参数名称")
    key: Optional[str] = Field(None, description="参数键名")
    type: Optional[int] = Field(None, ge=1, le=2, description="参数类型")
    visible: Optional[int] = Field(None, ge=0, le=1, description="是否可见")