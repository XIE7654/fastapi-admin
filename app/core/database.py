"""
数据库连接管理
使用 SQLAlchemy 2.0 异步模式
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy import event

from app.config import settings

# 异步引擎
engine: AsyncEngine = None

# 异步会话工厂
async_session_maker: async_sessionmaker[AsyncSession] = None

# 模型基类
Base = declarative_base()


async def init_db():
    """初始化数据库连接"""
    global engine, async_session_maker

    engine = create_async_engine(
        settings.DATABASE_URL,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_recycle=settings.DB_POOL_RECYCLE,
        echo=settings.DB_ECHO,
        pool_pre_ping=True,  # 检查连接是否有效
    )

    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


async def close_db():
    """关闭数据库连接"""
    global engine
    if engine:
        await engine.dispose()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话
    用于 FastAPI 依赖注入
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


class TenantQuery:
    """多租户查询混入类"""

    @classmethod
    def get_tenant_id(cls):
        """获取当前租户ID"""
        from app.core.tenant import get_tenant_id
        return get_tenant_id()

    def __init_subclass__(cls, **kwargs):
        """子类初始化时自动添加租户过滤"""
        super().__init_subclass__(**kwargs)