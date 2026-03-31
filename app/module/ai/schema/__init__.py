"""
AI 模块 Schema
"""
from app.module.ai.schema.api_key import (
    ApiKeyCreate,
    ApiKeyUpdate,
    ApiKeyResponse,
    ApiKeySimpleResponse,
    ApiKeyPageQuery,
)
from app.module.ai.schema.image import (
    ImagePageQuery,
    ImageUpdate,
    ImageResponse,
    ImageDrawReqVO,
)

__all__ = [
    "ApiKeyCreate",
    "ApiKeyUpdate",
    "ApiKeyResponse",
    "ApiKeySimpleResponse",
    "ApiKeyPageQuery",
    "ImagePageQuery",
    "ImageUpdate",
    "ImageResponse",
    "ImageDrawReqVO",
]