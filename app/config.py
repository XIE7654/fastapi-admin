"""
项目配置管理
使用 pydantic-settings 进行环境变量和配置管理
"""
from typing import Optional, List
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """应用配置"""

    # 应用基础配置
    APP_NAME: str = "芋道管理系统"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "基于FastAPI的企业级后台管理系统"
    DEBUG: bool = False
    API_PREFIX: str = "/admin-api"

    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 数据库配置
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "ruoyi-vue-pro"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 3600
    DB_ECHO: bool = False

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DATABASE_URL_SYNC(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Redis配置
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # JWT配置
    JWT_SECRET_KEY: str = "yudao-secret-key-please-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30天
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 多租户配置
    TENANT_ENABLE: bool = True
    TENANT_HEADER_NAME: str = "X-Tenant-Id"
    TENANT_IGNORE_URLS: List[str] = [
        "/admin-api/system/auth/login",
        "/admin-api/system/auth/logout",
        "/admin-api/system/auth/refresh-token",
        "/admin-api/system/captcha/**",
        "/admin-api/infra/file/**",
        "/admin-api/system/tenant/simple-list",
        "/admin-api/system/tenant/get-by-website",
    ]

    # 安全配置
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # 文件上传配置
    UPLOAD_MAX_SIZE: int = 16 * 1024 * 1024  # 16MB
    UPLOAD_ALLOWED_EXTENSIONS: List[str] = [
        "jpg", "jpeg", "png", "gif", "bmp", "webp",
        "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
        "txt", "zip", "rar"
    ]

    # 验证码配置
    CAPTCHA_EXPIRE_MINUTES: int = 5
    CAPTCHA_CACHE_TYPE: str = "redis"  # redis or local

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# 全局配置实例
settings = Settings()