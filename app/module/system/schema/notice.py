"""
通知公告相关 Schema
"""
from typing import Optional
from pydantic import Field, field_validator

from app.common.schema import CamelModel, CamelORMModel


class NoticeSave(CamelModel):
    """通知公告创建/更新请求"""

    id: Optional[int] = Field(None, description="公告ID（更新时需要）")
    title: str = Field(..., max_length=50, description="公告标题")
    content: Optional[str] = Field(None, description="公告内容")
    type: int = Field(..., ge=1, le=2, description="公告类型: 1-通知, 2-公告")
    status: Optional[int] = Field(default=0, ge=0, le=1, description="状态: 0-正常, 1-禁用")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("公告标题不能为空")
        return v.strip()


class NoticeResponse(CamelORMModel):
    """通知公告响应"""

    id: int = Field(..., description="公告ID")
    title: str = Field(..., description="公告标题")
    content: Optional[str] = Field(None, description="公告内容")
    type: int = Field(..., description="公告类型")
    status: int = Field(default=0, description="状态")
    create_time: Optional[str] = Field(None, description="创建时间")