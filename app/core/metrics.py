"""
监控指标服务
基于Prometheus实现
"""
from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response


# ==================== HTTP请求指标 ====================

# 请求总数
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

# 请求延迟
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# 正在处理的请求数
REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "HTTP requests in progress",
    ["method", "endpoint"]
)


# ==================== 业务指标 ====================

# 用户登录计数
USER_LOGIN_TOTAL = Counter(
    "user_login_total",
    "Total user logins",
    ["status"]
)

# API调用计数
API_CALL_TOTAL = Counter(
    "api_call_total",
    "Total API calls",
    ["api", "status"]
)

# 数据库连接池
DB_CONNECTIONS = Gauge(
    "db_connections",
    "Database connections",
    ["state"]
)

# Redis连接池
REDIS_CONNECTIONS = Gauge(
    "redis_connections",
    "Redis connections",
    ["state"]
)

# 缓存命中
CACHE_HITS = Counter(
    "cache_hits_total",
    "Cache hit count",
    ["cache_name"]
)

# 缓存未命中
CACHE_MISSES = Counter(
    "cache_misses_total",
    "Cache miss count",
    ["cache_name"]
)


# ==================== 系统指标 ====================

# 应用信息
APP_INFO = Info(
    "app",
    "Application information"
)

# 在线用户数
ONLINE_USERS = Gauge(
    "online_users",
    "Number of online users"
)


def track_request(method: str, endpoint: str, status: int):
    """记录请求指标"""
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()


def track_request_latency(method: str, endpoint: str, latency: float):
    """记录请求延迟"""
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency)


def track_request_start(method: str, endpoint: str):
    """记录请求开始"""
    REQUESTS_IN_PROGRESS.labels(method=method, endpoint=endpoint).inc()


def track_request_end(method: str, endpoint: str):
    """记录请求结束"""
    REQUESTS_IN_PROGRESS.labels(method=method, endpoint=endpoint).dec()


def track_user_login(success: bool = True):
    """记录用户登录"""
    status = "success" if success else "failed"
    USER_LOGIN_TOTAL.labels(status=status).inc()


def track_api_call(api: str, status: str = "success"):
    """记录API调用"""
    API_CALL_TOTAL.labels(api=api, status=status).inc()


def track_cache_hit(cache_name: str):
    """记录缓存命中"""
    CACHE_HITS.labels(cache_name=cache_name).inc()


def track_cache_miss(cache_name: str):
    """记录缓存未命中"""
    CACHE_MISSES.labels(cache_name=cache_name).inc()


def set_online_users(count: int):
    """设置在线用户数"""
    ONLINE_USERS.set(count)


def set_app_info(version: str, name: str):
    """设置应用信息"""
    APP_INFO.info({"version": version, "name": name})


async def metrics_endpoint():
    """Prometheus指标端点"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


class MetricsMiddleware:
    """指标收集中间件"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope["method"]
        path = scope["path"]

        # 排除指标端点本身
        if path == "/metrics":
            await self.app(scope, receive, send)
            return

        track_request_start(method, path)

        import time
        start_time = time.time()

        # 包装send以获取状态码
        status_code = 200

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            latency = time.time() - start_time
            track_request_end(method, path)
            track_request(method, path, status_code)
            track_request_latency(method, path, latency)