"""
岗位相关 Schema
"""
from typing import Optional
from pydantic import Field, field_validator

from app.common.schema import CamelModel, CamelORMModel
from app.common.pagination import PageQuery


class PostSave(CamelModel):
    """岗位创建/更新请求"""

    id: Optional[int] = Field(None, description="岗位ID（更新时需要）")
    name: str = Field(..., max_length=50, description="岗位名称")
    code: str = Field(..., max_length=64, description="岗位编码")
    sort: int = Field(default=0, description="显示顺序")
    status: Optional[int] = Field(default=0, ge=0, le=1, description="状态: 0-正常, 1-禁用")
    remark: Optional[str] = Field(None, max_length=500, description="备注")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("岗位名称不能为空")
        return v.strip()

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("岗位编码不能为空")
        return v.strip()


class PostResponse(CamelORMModel):
    """岗位响应"""

    id: int = Field(..., description="岗位ID")
    name: str = Field(..., description="岗位名称")
    code: str = Field(..., description="岗位编码")
    sort: int = Field(default=0, description="显示顺序")
    status: int = Field(default=0, description="状态")
    remark: Optional[str] = Field(None, description="备注")
    create_time: Optional[str] = Field(None, description="创建时间")


class PostSimpleResponse(CamelORMModel):
    """岗位简要响应"""

    id: int = Field(..., description="岗位ID")
    name: str = Field(..., description="岗位名称")
    code: str = Field(..., description="岗位编码")


class PostPageQuery(PageQuery):
    """岗位分页查询"""

    name: Optional[str] = Field(None, description="岗位名称")
    code: Optional[str] = Field(None, description="岗位编码")
    status: Optional[int] = Field(None, ge=0, le=1, description="状态")