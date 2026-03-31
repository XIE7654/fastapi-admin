"""
FastAPI 应用入口
"""
import logging
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
from app.middleware.demo import DemoMiddleware
from app.common.response import response_exception_handler
from app.common.exceptions import BusinessException

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    await init_db()

    # 导入模型基类以注册数据库事件监听器
    # 事件监听器使用 @event.listens_for 装饰器，在模块导入时自动注册
    import app.module.system.model.base

    # Redis 初始化失败不影响服务启动
    try:
        await init_redis()
    except Exception as e:
        logger.warning(f"Redis 初始化失败，将降级到数据库模式: {e}")

    # 初始化定时任务
    init_scheduler()
    start_scheduler()

    # 设置应用信息
    set_app_info(settings.APP_VERSION, settings.APP_NAME)

    yield

    # 关闭时清理
    shutdown_scheduler()
    await close_db()

    # 关闭 Redis 连接
    try:
        await close_redis()
    except Exception:
        pass


def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    app = FastAPI(
        title=settings.APP_NAME,
        description="基于FastAPI的企业级后台管理系统。业务逻辑借鉴自芋道 ruoyi-vue-pro 开源项目。",
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

    # 演示环境中间件
    if settings.DEMO_MODE:
        app.add_middleware(DemoMiddleware)

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
        log, config, online_user, tenant, notify_message, tenant_package,
        sms, sms_log, mail, notify_template, notice, area, social, oauth2,
        permission
    )
    from app.module.ai.controller import ai_model_router, api_key_router, chat_role_router, chat_message_router, image_router, tool_router

    # ====================
    # 认证管理
    # ====================
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

    # 字典类型管理
    app.include_router(dict.router_type, prefix=f"{settings.API_PREFIX}/system/dict-type", tags=["字典类型管理"])

    # 字典数据管理
    app.include_router(dict.router_data, prefix=f"{settings.API_PREFIX}/system/dict-data", tags=["字典数据管理"])

    # 操作日志
    app.include_router(log.router_operate, prefix=f"{settings.API_PREFIX}/system/operate-log", tags=["操作日志"])

    # 登录日志
    app.include_router(log.router_login, prefix=f"{settings.API_PREFIX}/system/login-log", tags=["登录日志"])

    # 参数配置
    app.include_router(config.router, prefix=f"{settings.API_PREFIX}/system/config", tags=["参数配置"])

    # 在线用户
    app.include_router(online_user.router, prefix=f"{settings.API_PREFIX}/system/online-user", tags=["在线用户"])

    # 租户管理
    app.include_router(tenant.router, prefix=f"{settings.API_PREFIX}/system/tenant", tags=["租户管理"])

    # 租户套餐管理
    app.include_router(tenant_package.router, prefix=f"{settings.API_PREFIX}/system/tenant-package", tags=["租户套餐管理"])

    # 站内信管理 (用户端操作)
    app.include_router(notify_message.router, prefix=f"{settings.API_PREFIX}/system/notify-message", tags=["站内信管理"])

    # 站内信模板管理
    app.include_router(notify_template.router_template, prefix=f"{settings.API_PREFIX}/system/notify-template", tags=["站内信模板管理"])

    # 站内信消息管理 (管理端分页)
    app.include_router(notify_template.router_message, prefix=f"{settings.API_PREFIX}/system/notify-message", tags=["站内信消息管理"])

    # 短信渠道管理
    app.include_router(sms.router_channel, prefix=f"{settings.API_PREFIX}/system/sms-channel", tags=["短信渠道管理"])

    # 短信模板管理
    app.include_router(sms.router_template, prefix=f"{settings.API_PREFIX}/system/sms-template", tags=["短信模板管理"])

    # 短信日志管理
    app.include_router(sms_log.router, prefix=f"{settings.API_PREFIX}/system/sms-log", tags=["短信日志管理"])

    # 邮箱账号管理
    app.include_router(mail.router_account, prefix=f"{settings.API_PREFIX}/system/mail-account", tags=["邮箱账号管理"])

    # 邮件模板管理
    app.include_router(mail.router_template, prefix=f"{settings.API_PREFIX}/system/mail-template", tags=["邮件模板管理"])

    # 邮件日志管理
    app.include_router(mail.router_log, prefix=f"{settings.API_PREFIX}/system/mail-log", tags=["邮件日志管理"])

    # 通知公告管理
    app.include_router(notice.router, prefix=f"{settings.API_PREFIX}/system/notice", tags=["通知公告管理"])

    # 地区管理
    app.include_router(area.router, prefix=f"{settings.API_PREFIX}/system/area", tags=["地区管理"])

    # 社交客户端管理
    app.include_router(social.router_client, prefix=f"{settings.API_PREFIX}/system/social-client", tags=["社交客户端管理"])

    # 社交用户管理
    app.include_router(social.router_user, prefix=f"{settings.API_PREFIX}/system/social-user", tags=["社交用户管理"])

    # OAuth2客户端管理
    app.include_router(oauth2.router_client, prefix=f"{settings.API_PREFIX}/system/oauth2-client", tags=["OAuth2客户端管理"])

    # OAuth2令牌管理
    app.include_router(oauth2.router_token, prefix=f"{settings.API_PREFIX}/system/oauth2-token", tags=["OAuth2令牌管理"])

    # 权限管理
    app.include_router(permission.router, prefix=f"{settings.API_PREFIX}/system/permission", tags=["权限管理"])

    # ====================
    # AI 模块
    # ====================

    # AI API 密钥管理
    app.include_router(api_key_router, prefix=f"{settings.API_PREFIX}/ai/api-key", tags=["AI API 密钥管理"])

    # AI 模型管理
    app.include_router(ai_model_router, prefix=f"{settings.API_PREFIX}/ai/model", tags=["AI 模型管理"])

    # AI 聊天角色管理
    app.include_router(chat_role_router, prefix=f"{settings.API_PREFIX}/ai/chat-role", tags=["AI 聊天角色管理"])

    # AI 聊天消息管理
    app.include_router(chat_message_router, prefix=f"{settings.API_PREFIX}/ai/chat/message", tags=["AI 聊天消息管理"])

    # AI 绘画管理
    app.include_router(image_router, prefix=f"{settings.API_PREFIX}/ai/image", tags=["AI 绘画管理"])

    # AI 工具管理
    app.include_router(tool_router, prefix=f"{settings.API_PREFIX}/ai/tool", tags=["AI 工具管理"])


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