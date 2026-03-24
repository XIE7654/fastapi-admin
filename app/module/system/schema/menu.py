"""
菜单相关 Schema
"""
from typing import Optional
from pydantic import Field, field_validator

from app.common.schema import CamelModel, CamelORMModel


class MenuSave(CamelModel):
    """菜单创建/更新请求"""

    id: Optional[int] = Field(None, description="菜单ID（更新时需要）")
    name: str = Field(..., max_length=50, description="菜单名称")
    permission: Optional[str] = Field(None, max_length=100, description="权限标识")
    type: int = Field(..., ge=1, le=3, description="菜单类型: 1-目录, 2-菜单, 3-按钮")
    sort: int = Field(default=0, description="显示顺序")
    parent_id: int = Field(default=0, description="父菜单ID")
    path: Optional[str] = Field(None, max_length=200, description="路由地址")
    icon: Optional[str] = Field(None, description="菜单图标")
    component: Optional[str] = Field(None, max_length=200, description="组件路径")
    component_name: Optional[str] = Field(None, description="组件名称")
    status: Optional[int] = Field(default=0, ge=0, le=1, description="状态: 0-正常, 1-禁用")
    visible: Optional[bool] = Field(default=True, description="是否可见")
    keep_alive: Optional[bool] = Field(default=False, description="是否缓存")
    always_show: Optional[bool] = Field(default=False, description="是否总是显示")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("菜单名称不能为空")
        return v.strip()


class MenuResponse(CamelORMModel):
    """菜单响应"""

    id: int = Field(..., description="菜单ID")
    name: str = Field(..., description="菜单名称")
    permission: Optional[str] = Field(None, description="权限标识")
    type: int = Field(..., description="菜单类型")
    sort: int = Field(default=0, description="显示顺序")
    parent_id: int = Field(default=0, description="父菜单ID")
    path: Optional[str] = Field(None, description="路由地址")
    icon: Optional[str] = Field(None, description="菜单图标")
    component: Optional[str] = Field(None, description="组件路径")
    component_name: Optional[str] = Field(None, description="组件名称")
    status: int = Field(default=0, description="状态")
    visible: bool = Field(default=True, description="是否可见")
    keep_alive: bool = Field(default=False, description="是否缓存")
    always_show: bool = Field(default=False, description="是否总是显示")
    create_time: Optional[str] = Field(None, description="创建时间")


class MenuSimpleResponse(CamelORMModel):
    """菜单简要响应"""

    id: int = Field(..., description="菜单ID")
    name: str = Field(..., description="菜单名称")
    parent_id: int = Field(default=0, description="父菜单ID")
    path: Optional[str] = Field(None, description="路由地址")