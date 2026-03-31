"""
AI 模型相关 Schema
"""
from typing import Optional, List
from datetime import datetime
from pydantic import Field, field_validator
from enum import Enum

from app.common.schema import CamelModel, CamelORMModel
from app.common.pagination import PageQuery


class AiPlatformEnum(str, Enum):
    """AI 模型平台枚举"""
    # 国内平台
    TONG_YI = "TongYi"  # 通义千问 - 阿里
    YI_YAN = "YiYan"  # 文心一言 - 百度
    DEEP_SEEK = "DeepSeek"  # DeepSeek
    ZHI_PU = "ZhiPu"  # 智谱 AI
    XING_HUO = "XingHuo"  # 星火 - 讯飞
    DOU_BAO = "DouBao"  # 豆包 - 字节
    HUN_YUAN = "HunYuan"  # 混元 - 腾讯
    SILICON_FLOW = "SiliconFlow"  # 硅基流动
    MINI_MAX = "MiniMax"  # MiniMax - 稀宇科技
    MOONSHOT = "Moonshot"  # 月之暗面 - KIMI
    BAI_CHUAN = "BaiChuan"  # 百川智能
    # 国外平台
    OPENAI = "OpenAI"  # OpenAI 官方
    AZURE_OPENAI = "AzureOpenAI"  # OpenAI 微软
    ANTHROPIC = "Anthropic"  # Anthropic Claude
    GEMINI = "Gemini"  # 谷歌 Gemini
    OLLAMA = "Ollama"
    STABLE_DIFFUSION = "StableDiffusion"  # Stability AI
    MIDJOURNEY = "Midjourney"  # Midjourney
    SUNO = "Suno"  # Suno AI
    GROK = "Grok"  # Grok


class AiModelTypeEnum(int, Enum):
    """AI 模型类型枚举"""
    CHAT = 1  # 对话
    IMAGE = 2  # 图片
    VOICE = 3  # 语音
    VIDEO = 4  # 视频
    EMBEDDING = 5  # 向量
    RERANK = 6  # 重排序


class AiModelBase(CamelModel):
    """AI 模型基础信息"""

    key_id: int = Field(..., description="API 秘钥编号")
    name: str = Field(..., max_length=64, description="模型名字")
    model: str = Field(..., max_length=64, description="模型标识")
    platform: str = Field(..., max_length=32, description="模型平台")
    type: int = Field(..., description="模型类型")
    sort: int = Field(..., description="排序")
    status: int = Field(..., ge=0, le=1, description="状态: 0-开启, 1-禁用")
    temperature: Optional[float] = Field(None, description="温度参数")
    max_tokens: Optional[int] = Field(None, description="单条回复的最大 Token 数量")
    max_contexts: Optional[int] = Field(None, description="上下文的最大 Message 数量")

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, v: str) -> str:
        """验证平台"""
        valid_platforms = [e.value for e in AiPlatformEnum]
        if v not in valid_platforms:
            raise ValueError(f"非法平台: {v}")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: int) -> int:
        """验证模型类型"""
        valid_types = [e.value for e in AiModelTypeEnum]
        if v not in valid_types:
            raise ValueError(f"非法模型类型: {v}")
        return v


class AiModelCreate(AiModelBase):
    """创建 AI 模型请求"""

    pass


class AiModelUpdate(CamelModel):
    """更新 AI 模型请求"""

    id: int = Field(..., description="模型编号")
    key_id: Optional[int] = Field(None, description="API 秘钥编号")
    name: Optional[str] = Field(None, max_length=64, description="模型名字")
    model: Optional[str] = Field(None, max_length=64, description="模型标识")
    platform: Optional[str] = Field(None, max_length=32, description="模型平台")
    type: Optional[int] = Field(None, description="模型类型")
    sort: Optional[int] = Field(None, description="排序")
    status: Optional[int] = Field(None, ge=0, le=1, description="状态")
    temperature: Optional[float] = Field(None, description="温度参数")
    max_tokens: Optional[int] = Field(None, description="单条回复的最大 Token 数量")
    max_contexts: Optional[int] = Field(None, description="上下文的最大 Message 数量")

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, v: Optional[str]) -> Optional[str]:
        """验证平台"""
        if v is None:
            return v
        valid_platforms = [e.value for e in AiPlatformEnum]
        if v not in valid_platforms:
            raise ValueError(f"非法平台: {v}")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: Optional[int]) -> Optional[int]:
        """验证模型类型"""
        if v is None:
            return v
        valid_types = [e.value for e in AiModelTypeEnum]
        if v not in valid_types:
            raise ValueError(f"非法模型类型: {v}")
        return v


class AiModelResponse(CamelORMModel):
    """AI 模型响应"""

    id: int = Field(..., description="编号")
    key_id: Optional[int] = Field(None, description="API 秘钥编号")
    name: Optional[str] = Field(None, description="模型名字")
    model: Optional[str] = Field(None, description="模型标识")
    platform: Optional[str] = Field(None, description="模型平台")
    type: Optional[int] = Field(None, description="模型类型")
    sort: Optional[int] = Field(None, description="排序")
    status: Optional[int] = Field(None, description="状态")
    temperature: Optional[float] = Field(None, description="温度参数")
    max_tokens: Optional[int] = Field(None, description="单条回复的最大 Token 数量")
    max_contexts: Optional[int] = Field(None, description="上下文的最大 Message 数量")
    create_time: Optional[datetime] = Field(None, description="创建时间")


class AiModelSimpleResponse(CamelORMModel):
    """AI 模型简要响应"""

    id: int = Field(..., description="编号")
    name: Optional[str] = Field(None, description="模型名字")
    model: Optional[str] = Field(None, description="模型标识")
    platform: Optional[str] = Field(None, description="模型平台")


class AiModelPageQuery(PageQuery):
    """AI 模型分页查询"""

    name: Optional[str] = Field(None, description="模型名字")
    model: Optional[str] = Field(None, description="模型标识")
    platform: Optional[str] = Field(None, description="模型平台")