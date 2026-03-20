"""
FastAPI 应用入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.database import init_db, close_db
from app.core.redis import init_redis, close_redis
from app.core.scheduler import init_scheduler, start_scheduler, shutdown_scheduler
from app.core.metrics import set_app_info, metrics_endpoint
from app.middleware.tenant import TenantMiddleware
from app.middleware.logging import LoggingMiddleware
from app.common.response import response_exception_handler
from app.common.exceptions import BusinessException


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    await init_db()
    await init_redis()

    # 初始化定时任务
    init_scheduler()
    start_scheduler()

    # 设置应用信息
    set_app_info(settings.APP_VERSION, settings.APP_NAME)

    yield

    # 关闭时清理
    shutdown_scheduler()
    await close_db()
    await close_redis()


def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    app = FastAPI(
        title=settings.APP_NAME,
        description="基于FastAPI的企业级后台管理系统，迁移自芋道Java项目",
        version=settings.APP_VERSION,
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        docs_url=f"{settings.API_PREFIX}/docs",
        redoc_url=f"{settings.API_PREFIX}/redoc",
        lifespan=lifespan,
    )

    # CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    # 多租户中间件
    if settings.TENANT_ENABLE:
        app.add_middleware(TenantMiddleware)

    # 日志中间件
    app.add_middleware(LoggingMiddleware)

    # 全局异常处理
    app.add_exception_handler(BusinessException, response_exception_handler)

    # 注册路由
    register_routers(app)

    # 注册监控端点
    app.add_route("/metrics", metrics_endpoint, methods=["GET"])

    return app


def register_routers(app: FastAPI):
    """注册所有路由"""
    from app.module.system.controller import (
        auth, user, role, menu, dept, dict, post,
        log, config, online_user, tenant
    )

    # 认证管理
    app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/system/auth", tags=["认证管理"])

    # 用户管理
    app.include_router(user.router, prefix=f"{settings.API_PREFIX}/system/user", tags=["用户管理"])

    # 角色管理
    app.include_router(role.router, prefix=f"{settings.API_PREFIX}/system/role", tags=["角色管理"])

    # 菜单管理
    app.include_router(menu.router, prefix=f"{settings.API_PREFIX}/system/menu", tags=["菜单管理"])

    # 部门管理
    app.include_router(dept.router, prefix=f"{settings.API_PREFIX}/system/dept", tags=["部门管理"])

    # 岗位管理
    app.include_router(post.router, prefix=f"{settings.API_PREFIX}/system/post", tags=["岗位管理"])

    # 字典管理
    app.include_router(dict.router, prefix=f"{settings.API_PREFIX}/system/dict", tags=["字典管理"])

    # 日志管理
    app.include_router(log.router, prefix=f"{settings.API_PREFIX}/system/log", tags=["日志管理"])

    # 参数配置
    app.include_router(config.router, prefix=f"{settings.API_PREFIX}/system/config", tags=["参数配置"])

    # 在线用户
    app.include_router(online_user.router, prefix=f"{settings.API_PREFIX}/system/online-user", tags=["在线用户"])

    # 租户管理
    app.include_router(tenant.router, prefix=f"{settings.API_PREFIX}/system/tenant", tags=["租户管理"])


# 创建应用实例
app = create_app()


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "version": settings.APP_VERSION}


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": f"{settings.API_PREFIX}/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )