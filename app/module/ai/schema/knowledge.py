"""
AI 知识库相关 Schema
参考 ruoyi-vue-pro yudao-module-ai AiKnowledgePageReqVO、AiKnowledgeRespVO、AiKnowledgeSaveReqVO
"""
from typing import Optional, List, Any
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


class KnowledgePageQuery(PageQuery):
    """AI 知识库分页查询"""

    name: Optional[str] = Field(None, description="知识库名称")
    status: Optional[int] = Field(None, ge=0, le=1, description="状态")


class KnowledgeCreate(CamelModel):
    """创建 AI 知识库请求"""

    name: str = Field(..., max_length=255, description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")
    embedding_model_id: int = Field(..., description="向量模型编号")
    embedding_model: str = Field(..., max_length=32, description="向量模型标识")
    top_k: int = Field(..., description="topK")
    similarity_threshold: float = Field(..., description="相似度阈值")
    status: int = Field(..., ge=0, le=1, description="状态")


class KnowledgeUpdate(CamelModel):
    """更新 AI 知识库请求"""

    id: int = Field(..., description="知识库编号")
    name: Optional[str] = Field(None, max_length=255, description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")
    embedding_model_id: Optional[int] = Field(None, description="向量模型编号")
    embedding_model: Optional[str] = Field(None, max_length=32, description="向量模型标识")
    top_k: Optional[int] = Field(None, description="topK")
    similarity_threshold: Optional[float] = Field(None, description="相似度阈值")
    status: Optional[int] = Field(None, ge=0, le=1, description="状态")


class KnowledgeResponse(CamelORMModel):
    """AI 知识库响应"""

    id: int = Field(..., description="编号")
    name: Optional[str] = Field(None, description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")
    embedding_model_id: Optional[int] = Field(None, description="向量模型编号")
    embedding_model: Optional[str] = Field(None, description="向量模型标识")
    top_k: Optional[int] = Field(None, description="topK")
    similarity_threshold: Optional[float] = Field(None, description="相似度阈值")
    status: Optional[int] = Field(None, description="状态")
    create_time: Optional[datetime] = Field(None, description="创建时间")

    @field_validator('status', mode='before')
    @classmethod
    def validate_bit_field(cls, v: Any) -> Optional[int]:
        """处理 MySQL BIT 类型字段"""
        return convert_bit_to_int(v)


class KnowledgeSimpleResponse(CamelORMModel):
    """AI 知识库简要响应（用于前端下拉选项）"""

    id: int = Field(..., description="编号")
    name: Optional[str] = Field(None, description="知识库名称")