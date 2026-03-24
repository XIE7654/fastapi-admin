"""
字典相关 Schema
"""
from typing import Optional
from pydantic import Field, field_validator

from app.common.schema import CamelModel, CamelORMModel
from app.common.pagination import PageQuery


class DictTypeSave(CamelModel):
    """字典类型创建/更新请求"""

    id: Optional[int] = Field(None, description="字典类型ID（更新时需要）")
    name: str = Field(..., max_length=100, description="字典名称")
    type: str = Field(..., max_length=100, description="字典类型")
    status: Optional[int] = Field(default=0, ge=0, le=1, description="状态: 0-正常, 1-禁用")
    remark: Optional[str] = Field(None, max_length=500, description="备注")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("字典名称不能为空")
        return v.strip()

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("字典类型不能为空")
        return v.strip()


class DictTypeResponse(CamelORMModel):
    """字典类型响应"""

    id: int = Field(..., description="字典类型ID")
    name: str = Field(..., description="字典名称")
    type: str = Field(..., description="字典类型")
    status: int = Field(default=0, description="状态")
    remark: Optional[str] = Field(None, description="备注")
    create_time: Optional[str] = Field(None, description="创建时间")


class DictDataSave(CamelModel):
    """字典数据创建/更新请求"""

    id: Optional[int] = Field(None, description="字典数据ID（更新时需要）")
    sort: int = Field(default=0, description="显示顺序")
    label: str = Field(..., max_length=100, description="字典标签")
    value: str = Field(..., max_length=100, description="字典键值")
    dict_type: str = Field(..., max_length=100, description="字典类型")
    status: Optional[int] = Field(default=0, ge=0, le=1, description="状态: 0-正常, 1-禁用")
    color_type: Optional[str] = Field(None, description="颜色类型")
    css_class: Optional[str] = Field(None, description="CSS类名")
    remark: Optional[str] = Field(None, max_length=500, description="备注")

    @field_validator("label")
    @classmethod
    def validate_label(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("字典标签不能为空")
        return v.strip()

    @field_validator("value")
    @classmethod
    def validate_value(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("字典键值不能为空")
        return v.strip()

    @field_validator("dict_type")
    @classmethod
    def validate_dict_type(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("字典类型不能为空")
        return v.strip()


class DictDataResponse(CamelORMModel):
    """字典数据响应"""

    id: int = Field(..., description="字典数据ID")
    sort: int = Field(default=0, description="显示顺序")
    label: str = Field(..., description="字典标签")
    value: str = Field(..., description="字典键值")
    dict_type: str = Field(..., description="字典类型")
    status: int = Field(default=0, description="状态")
    color_type: Optional[str] = Field(None, description="颜色类型")
    css_class: Optional[str] = Field(None, description="CSS类名")
    remark: Optional[str] = Field(None, description="备注")
    create_time: Optional[str] = Field(None, description="创建时间")


class DictTypePageQuery(PageQuery):
    """字典类型分页查询"""

    name: Optional[str] = Field(None, description="字典名称")
    type: Optional[str] = Field(None, description="字典类型")
    status: Optional[int] = Field(None, ge=0, le=1, description="状态")


class DictDataPageQuery(PageQuery):
    """字典数据分页查询"""

    label: Optional[str] = Field(None, description="字典标签")
    dict_type: Optional[str] = Field(None, description="字典类型")
    status: Optional[int] = Field(None, ge=0, le=1, description="状态")