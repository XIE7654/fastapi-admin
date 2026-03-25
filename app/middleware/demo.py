"""
演示环境中间件
在演示环境下拦截写操作（POST/PUT/DELETE）
"""
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.common.exceptions import BusinessException, ErrorCode


class DemoMiddleware(BaseHTTPMiddleware):
    """演示环境中间件"""

    # 允许的写操作路径（登录、登出等）
    ALLOWED_PATHS = [
        "/admin-api/system/auth/login",
        "/admin-api/system/auth/logout",
        "/admin-api/system/auth/refresh-token",
    ]

    # 写操作方法
    WRITE_METHODS = {"POST", "PUT", "DELETE", "PATCH"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        # 非演示环境，直接放行
        if not settings.DEMO_MODE:
            return await call_next(request)

        # GET 请求直接放行
        if request.method == "GET":
            return await call_next(request)

        # 检查是否是写操作
        if request.method in self.WRITE_METHODS:
            # 检查是否在允许列表中
            path = request.url.path
            if any(path.startswith(allowed) for allowed in self.ALLOWED_PATHS):
                return await call_next(request)

            # 演示环境禁止写操作
            raise BusinessException(
                code=ErrorCode.DEMO_DENY,
                message="演示环境，禁止写入操作"
            )

        return await call_next(request)