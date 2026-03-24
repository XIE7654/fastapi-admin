"""
租户套餐相关 Schema
"""
from typing import Optional, List
from datetime import datetime
from pydantic import Field, field_validator

from app.common.schema import CamelModel, CamelORMModel
from app.common.pagination import PageQuery


class TenantPackageSaveReqVO(CamelModel):
    """租户套餐创建/修改请求"""

    id: Optional[int] = Field(None, description="套餐编号（更新时需要）")
    name: str = Field(..., max_length=30, description="套餐名称")
    status: int = Field(..., ge=0, le=1, description="状态: 0-正常, 1-禁用")
    remark: Optional[str] = Field(None, max_length=256, description="备注")
    menu_ids: List[int] = Field(..., description="关联的菜单编号列表")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("套餐名不能为空")
        return v.strip()

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: int) -> int:
        if v not in [0, 1]:
            raise ValueError("状态必须是 0 或 1")
        return v


class TenantPackagePageReqVO(PageQuery):
    """租户套餐分页请求"""

    name: Optional[str] = Field(None, description="套餐名称")
    status: Optional[int] = Field(None, description="状态")
    remark: Optional[str] = Field(None, description="备注")
    create_time: Optional[List[datetime]] = Field(None, description="创建时间")


class TenantPackageRespVO(CamelORMModel):
    """租户套餐响应"""

    id: int = Field(..., description="套餐编号")
    name: str = Field(..., description="套餐名称")
    status: int = Field(..., description="状态: 0-正常, 1-禁用")
    remark: Optional[str] = Field(None, description="备注")
    menu_ids: List[int] = Field(default_factory=list, description="关联的菜单编号列表")
    create_time: datetime = Field(..., description="创建时间")


class TenantPackageSimpleRespVO(CamelORMModel):
    """租户套餐精简响应"""

    id: int = Field(..., description="套餐编号")
    name: str = Field(..., description="套餐名称")