"""
日志中间件
记录请求和响应日志
"""
import time
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件"""

    # 不记录日志的路径
    IGNORE_PATHS = [
        "/health",
        "/metrics",
        "/favicon.ico",
    ]

    # 不记录请求体的Content-Type
    IGNORE_BODY_TYPES = [
        "multipart/form-data",
        "application/octet-stream",
    ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        # 检查是否忽略
        if request.url.path in self.IGNORE_PATHS:
            return await call_next(request)

        # 记录开始时间
        start_time = time.time()

        # 记录请求信息
        request_info = {
            "method": request.method,
            "path": request.url.path,
            "query": dict(request.query_params),
            "client": request.client.host if request.client else None,
        }

        # 请求体（仅对JSON请求）
        content_type = request.headers.get("content-type", "")
        if not any(t in content_type for t in self.IGNORE_BODY_TYPES):
            try:
                body = await request.body()
                if body:
                    request_info["body"] = body.decode("utf-8")[:500]  # 限制长度
            except Exception:
                pass

        logger.info(f"Request: {json.dumps(request_info, ensure_ascii=False)}")

        # 调用下一个处理器
        response = await call_next(request)

        # 计算耗时
        process_time = (time.time() - start_time) * 1000

        # 记录响应信息
        response_info = {
            "status_code": response.status_code,
            "process_time_ms": round(process_time, 2),
        }

        # 添加处理时间头
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"

        logger.info(f"Response: {json.dumps(response_info, ensure_ascii=False)}")

        return response