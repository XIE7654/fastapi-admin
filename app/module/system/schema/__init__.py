"""
Schema模块 - Pydantic数据模型
"""
from app.module.system.schema.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserPageQuery,
)
from app.module.system.schema.auth import (
    LoginRequest,
    LoginResponse,
    TokenResponse,
)
from app.module.system.schema.log import (
    OperateLogPageQuery,
    OperateLogResponse,
    LoginLogPageQuery,
    LoginLogResponse,
)
from app.module.system.schema.config import (
    ConfigCreate,
    ConfigUpdate,
    ConfigResponse,
    ConfigPageQuery,
)

__all__ = [
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserPageQuery",
    # Auth
    "LoginRequest",
    "LoginResponse",
    "TokenResponse",
    # Log
    "OperateLogPageQuery",
    "OperateLogResponse",
    "LoginLogPageQuery",
    "LoginLogResponse",
    # Config
    "ConfigCreate",
    "ConfigUpdate",
    "ConfigResponse",
    "ConfigPageQuery",
]