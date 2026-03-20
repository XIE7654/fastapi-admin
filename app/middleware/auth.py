"""
认证中间件
可选的请求级别认证处理
"""
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.security import verify_token
from app.core.tenant import set_tenant


class AuthMiddleware(BaseHTTPMiddleware):
    """
    认证中间件
    注意：大多数情况下推荐使用 Depends(get_current_user) 依赖注入
    此中间件适用于需要全局认证的场景
    """

    # 不需要认证的路径
    PUBLIC_PATHS = [
        "/admin-api/system/auth/login",
        "/admin-api/system/auth/logout",
        "/admin-api/system/auth/refresh-token",
        "/admin-api/system/captcha/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
    ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        # 检查是否是公开路径
        if self._is_public_path(request.url.path):
            return await call_next(request)

        # 从请求头获取Token
        authorization = request.headers.get("Authorization")
        if not authorization:
            return await call_next(request)

        # 解析Bearer Token
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return await call_next(request)

        token = parts[1]

        # 验证Token
        payload = verify_token(token, token_type="access")
        if payload:
            # 将用户信息存储到请求状态
            request.state.user_id = payload.get("user_id")
            request.state.username = payload.get("sub")

            # 设置租户上下文
            tenant_id = payload.get("tenant_id")
            if tenant_id:
                set_tenant(tenant_id)

        return await call_next(request)

    def _is_public_path(self, path: str) -> bool:
        """检查是否是公开路径"""
        for public_path in self.PUBLIC_PATHS:
            if path.startswith(public_path):
                return True
        return False