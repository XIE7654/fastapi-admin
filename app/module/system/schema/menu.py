"""
菜单相关 Schema
"""
from typing import Optional, Union
from pydantic import Field, field_validator

from app.common.schema import CamelModel, CamelORMModel


def parse_bool(v: Union[bool, int, str, None]) -> Union[bool, None]:
    """解析布尔值，支持多种格式"""
    if v is None:
        return None  # 返回 None 让 Pydantic 使用字段默认值
    if isinstance(v, bool):
        return v
    if isinstance(v, int):
        return v != 0
    if isinstance(v, str):
        # 处理 MySQL tinyint(1) 存储的 "\x00" 和 "\x01"
        if v == "\x00":
            return False
        if v == "\x01":
            return True
        # 处理字符串 "0", "1", "true", "false"
        if v.lower() in ("0", "false", ""):
            return False
        if v.lower() in ("1", "true"):
            return True
        # 其他情况转换为 int 再判断
        try:
            return int(v) != 0
        except ValueError:
            return bool(v)
    return bool(v)


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

    @field_validator("visible", "keep_alive", "always_show", mode="before")
    @classmethod
    def validate_bool_fields(cls, v):
        """解析布尔字段，支持 MySQL tinyint 格式"""
        return parse_bool(v)


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