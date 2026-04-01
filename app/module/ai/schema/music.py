"""
AI 音乐相关 Schema
参考 ruoyi-vue-pro yudao-module-ai 模块的 AiMusicPageReqVO、AiMusicRespVO
"""
from typing import Optional, List, Any
from datetime import datetime
from pydantic import Field, field_validator

from app.common.schema import CamelModel, CamelORMModel
from app.common.pagination import PageQuery


class MusicPageQuery(PageQuery):
    """AI 音乐分页查询"""

    user_id: Optional[int] = Field(None, description="用户编号")
    title: Optional[str] = Field(None, description="音乐名称")
    status: Optional[int] = Field(None, description="音乐状态")
    generate_mode: Optional[int] = Field(None, description="生成模式")
    public_status: Optional[bool] = Field(None, description="是否发布")


class MusicUpdateMy(CamelModel):
    """更新【我的】音乐请求"""

    id: int = Field(..., description="音乐编号")
    title: str = Field(..., max_length=200, description="音乐名称")


class MusicUpdate(CamelModel):
    """更新音乐请求（管理端）"""

    id: int = Field(..., description="音乐编号")
    title: Optional[str] = Field(None, max_length=200, description="音乐名称")
    public_status: Optional[int] = Field(None, description="是否发布: 0-否, 1-是")


def convert_bit_to_int(v: Any) -> Optional[int]:
    """将 MySQL BIT 类型转换为整数"""
    if v is None:
        return None
    if isinstance(v, bytes):
        return int.from_bytes(v, byteorder='big')
    if isinstance(v, bool):
        return 1 if v else 0
    return int(v)


class MusicResponse(CamelORMModel):
    """AI 音乐响应"""

    id: int = Field(..., description="编号")
    user_id: Optional[int] = Field(None, description="用户编号")
    title: Optional[str] = Field(None, description="音乐名称")
    lyric: Optional[str] = Field(None, description="歌词")
    image_url: Optional[str] = Field(None, description="图片地址")
    audio_url: Optional[str] = Field(None, description="音频地址")
    video_url: Optional[str] = Field(None, description="视频地址")
    status: Optional[int] = Field(None, description="音乐状态")
    description: Optional[str] = Field(None, description="描述词")
    prompt: Optional[str] = Field(None, description="提示词")
    platform: Optional[str] = Field(None, description="模型平台")
    model_id: Optional[int] = Field(None, description="模型编号")
    model: Optional[str] = Field(None, description="模型")
    generate_mode: Optional[int] = Field(None, description="生成模式")
    tags: Optional[str] = Field(None, description="音乐风格标签")
    duration: Optional[float] = Field(None, description="音乐时长")
    public_status: Optional[int] = Field(None, description="是否发布: 0-否, 1-是")
    task_id: Optional[str] = Field(None, description="任务编号")
    error_message: Optional[str] = Field(None, description="错误信息")
    create_time: Optional[datetime] = Field(None, description="创建时间")

    @field_validator('public_status', 'status', mode='before')
    @classmethod
    def validate_bit_field(cls, v: Any) -> Optional[int]:
        """处理 MySQL BIT 类型字段"""
        return convert_bit_to_int(v)