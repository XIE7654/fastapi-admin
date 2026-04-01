"""
AI 绘画相关 Schema
参考 ruoyi-vue-pro yudao-module-ai 模块的 AiImagePageReqVO、AiImageRespVO、AiImageUpdateReqVO
"""
from typing import Optional, List, Dict, Any
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


class ImagePageQuery(PageQuery):
    """AI 绘画分页查询"""

    user_id: Optional[int] = Field(None, description="用户编号")
    platform: Optional[str] = Field(None, description="平台")
    prompt: Optional[str] = Field(None, description="提示词")
    status: Optional[int] = Field(None, description="绘画状态")
    public_status: Optional[int] = Field(None, description="是否发布")


class ImageUpdate(CamelModel):
    """AI 绘画修改请求"""

    id: int = Field(..., description="编号")
    public_status: Optional[int] = Field(None, description="是否发布: 0-否, 1-是")


class ImageResponse(CamelORMModel):
    """AI 绘画响应"""

    id: int = Field(..., description="编号")
    user_id: Optional[int] = Field(None, description="用户编号")
    prompt: Optional[str] = Field(None, description="提示词")
    platform: Optional[str] = Field(None, description="平台")
    model_id: Optional[int] = Field(None, description="模型编号")
    model: Optional[str] = Field(None, description="模型")
    width: Optional[int] = Field(None, description="图片宽度")
    height: Optional[int] = Field(None, description="图片高度")
    status: Optional[int] = Field(None, description="绘画状态")
    finish_time: Optional[datetime] = Field(None, description="完成时间")
    error_message: Optional[str] = Field(None, description="错误信息")
    public_status: Optional[int] = Field(None, description="是否发布")
    pic_url: Optional[str] = Field(None, description="图片地址")
    options: Optional[Dict[str, Any]] = Field(None, description="绘制参数")
    task_id: Optional[str] = Field(None, description="任务编号")
    buttons: Optional[str] = Field(None, description="mj buttons 按钮")
    create_time: Optional[datetime] = Field(None, description="创建时间")

    @field_validator('public_status', 'status', mode='before')
    @classmethod
    def validate_bit_field(cls, v: Any) -> Optional[int]:
        """处理 MySQL BIT 类型字段"""
        return convert_bit_to_int(v)


class ImageDrawReqVO(CamelModel):
    """AI 绘画生成请求"""

    platform: str = Field(..., description="平台")
    model: Optional[str] = Field(None, description="模型")
    prompt: str = Field(..., description="提示词")
    width: int = Field(default=1024, description="图片宽度")
    height: int = Field(default=1024, description="图片高度")
    options: Optional[Dict[str, Any]] = Field(None, description="绘制参数")