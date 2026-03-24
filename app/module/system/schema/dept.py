"""
部门相关 Schema
"""
from typing import Optional
from pydantic import Field, field_validator

from app.common.schema import CamelModel, CamelORMModel


class DeptSave(CamelModel):
    """部门创建/更新请求"""

    id: Optional[int] = Field(None, description="部门ID（更新时需要）")
    name: str = Field(..., max_length=30, description="部门名称")
    parent_id: int = Field(default=0, description="父部门ID")
    sort: int = Field(default=0, description="显示顺序")
    leader_user_id: Optional[int] = Field(None, description="负责人用户ID")
    phone: Optional[str] = Field(None, max_length=11, description="联系电话")
    email: Optional[str] = Field(None, max_length=50, description="邮箱")
    status: Optional[int] = Field(default=0, ge=0, le=1, description="状态: 0-正常, 1-禁用")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("部门名称不能为空")
        return v.strip()


class DeptResponse(CamelORMModel):
    """部门响应"""

    id: int = Field(..., description="部门ID")
    name: str = Field(..., description="部门名称")
    parent_id: int = Field(default=0, description="父部门ID")
    sort: int = Field(default=0, description="显示顺序")
    leader_user_id: Optional[int] = Field(None, description="负责人用户ID")
    phone: Optional[str] = Field(None, description="联系电话")
    email: Optional[str] = Field(None, description="邮箱")
    status: int = Field(default=0, description="状态")
    create_time: Optional[str] = Field(None, description="创建时间")


class DeptSimpleResponse(CamelORMModel):
    """部门简要响应"""

    id: int = Field(..., description="部门ID")
    name: str = Field(..., description="部门名称")
    parent_id: int = Field(default=0, description="父部门ID")