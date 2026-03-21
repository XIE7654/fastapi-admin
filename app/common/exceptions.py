"""
异常定义模块（重新导出核心异常）
"""
from app.core.exceptions import (
    BusinessException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    ValidationException,
    TenantException,
    AuthenticationException,
    ErrorCode,
)

__all__ = [
    "BusinessException",
    "UnauthorizedException",
    "ForbiddenException",
    "NotFoundException",
    "ValidationException",
    "TenantException",
    "AuthenticationException",
    "ErrorCode",
]