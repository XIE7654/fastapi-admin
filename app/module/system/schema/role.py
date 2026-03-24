"""
角色相关 Schema
"""
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, AliasGenerator

from app.common.pagination import to_camel


class RoleSave(BaseModel):
    """角色创建/更新请求"""

    model_config = {
        "populate_by_name": True,
        "alias_generator": AliasGenerator(
            serialization_alias=to_camel,
            validation_alias=to_camel,
        ),
    }

    id: Optional[int] = Field(None, description="角色ID（更新时需要）")
    name: str = Field(..., max_length=30, description="角色名称")
    code: str = Field(..., max_length=100, description="角色编码")
    sort: int = Field(default=0, description="显示顺序")
    status: Optional[int] = Field(default=0, ge=0, le=1, description="状态: 0-正常, 1-禁用")
    data_scope: Optional[int] = Field(default=1, ge=1, le=5, description="数据范围: 1-全部, 2-自定义, 3-本部门, 4-本部门及以下, 5-仅本人")
    data_scope_dept_ids: Optional[str] = Field(None, max_length=500, description="数据范围部门ID列表")
    remark: Optional[str] = Field(None, max_length=500, description="备注")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("角色名称不能为空")
        return v.strip()

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("角色编码不能为空")
        return v.strip()