"""
多租户中间件
从请求头中提取租户ID并设置上下文
"""
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.core.tenant import set_tenant, clear_tenant
from app.core.exceptions import TenantException


class TenantMiddleware(BaseHTTPMiddleware):
    """多租户中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        # 检查是否是忽略的URL
        if self._should_ignore(request.url.path):
            return await call_next(request)

        # 从请求头获取租户ID
        tenant_id = request.headers.get(settings.TENANT_HEADER_NAME)

        if tenant_id:
            try:
                tenant_id = int(tenant_id)
                if tenant_id <= 0:
                    raise ValueError("Invalid tenant ID")
            except ValueError:
                raise TenantException("无效的租户ID")

            # 设置租户上下文
            set_tenant(tenant_id)

        try:
            response = await call_next(request)
        finally:
            # 清理租户上下文
            clear_tenant()

        return response

    def _should_ignore(self, path: str) -> bool:
        """检查是否应该忽略租户处理"""
        for pattern in settings.TENANT_IGNORE_URLS:
            # 简单的通配符匹配
            if pattern.endswith("/**"):
                prefix = pattern[:-3]
                if path.startswith(prefix):
                    return True
            elif path == pattern:
                return True
        return False