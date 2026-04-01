"""
AI 工作流相关 Schema
参考 ruoyi-vue-pro yudao-module-ai 模块的 AiWorkflowPageReqVO、AiWorkflowRespVO、AiWorkflowSaveReqVO
"""
from typing import Optional, Any
from datetime import datetime
from pydantic import Field, field_validator

from app.common.schema import CamelModel, CamelORMModel
from app.common.pagination import PageQuery


def convert_bit_to_int(v: Any) -> Optional[int]:
    """将 MySQL BIT 类型转换为整数"""
    if v is None:
        return None
    if isinstance(v, bytes):
        return int.from_bytes(v, byteorder='big')
    if isinstance(v, bool):
        return 1 if v else 0
    return int(v)


class WorkflowPageQuery(PageQuery):
    """AI 工作流分页查询"""

    name: Optional[str] = Field(None, description="工作流名称")
    code: Optional[str] = Field(None, description="工作流标识")
    status: Optional[int] = Field(None, description="状态")


class WorkflowCreate(CamelModel):
    """创建 AI 工作流请求"""

    code: str = Field(..., max_length=255, description="工作流标识")
    name: str = Field(..., max_length=255, description="工作流名称")
    graph: str = Field(..., description="工作流模型 JSON")
    status: int = Field(..., description="状态")
    remark: Optional[str] = Field(None, max_length=256, description="备注")


class WorkflowUpdate(CamelModel):
    """更新 AI 工作流请求"""

    id: int = Field(..., description="编号")
    code: Optional[str] = Field(None, max_length=255, description="工作流标识")
    name: Optional[str] = Field(None, max_length=255, description="工作流名称")
    graph: Optional[str] = Field(None, description="工作流模型 JSON")
    status: Optional[int] = Field(None, description="状态")
    remark: Optional[str] = Field(None, max_length=256, description="备注")


class WorkflowResponse(CamelORMModel):
    """AI 工作流响应"""

    id: int = Field(..., description="编号")
    code: Optional[str] = Field(None, description="工作流标识")
    name: Optional[str] = Field(None, description="工作流名称")
    graph: Optional[str] = Field(None, description="工作流模型 JSON")
    status: Optional[int] = Field(None, description="状态")
    remark: Optional[str] = Field(None, description="备注")
    create_time: Optional[datetime] = Field(None, description="创建时间")

    @field_validator('status', mode='before')
    @classmethod
    def validate_bit_field(cls, v: Any) -> Optional[int]:
        """处理 MySQL BIT 类型字段"""
        return convert_bit_to_int(v)