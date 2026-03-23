"""
Redis 连接管理
"""
from typing import Optional
import redis.asyncio as redis
from redis.asyncio import Redis

from app.config import settings


class RedisNotAvailableError(Exception):
    """Redis 不可用异常"""
    pass


# Redis 连接池
redis_pool: Optional[redis.ConnectionPool] = None
redis_client: Optional[Redis] = None


async def init_redis():
    """初始化Redis连接"""
    global redis_pool, redis_client

    redis_pool = redis.ConnectionPool(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DB,
        decode_responses=True,
        max_connections=50,
    )

    redis_client = Redis(connection_pool=redis_pool)

    # 测试连接
    await redis_client.ping()


async def close_redis():
    """关闭Redis连接"""
    global redis_pool, redis_client

    if redis_client:
        await redis_client.close()
    if redis_pool:
        await redis_pool.disconnect()


async def get_redis() -> Redis:
    """
    获取Redis客户端
    用于 FastAPI 依赖注入

    :raises RedisNotAvailableError: Redis 未初始化或不可用
    """
    if redis_client is None:
        raise RedisNotAvailableError("Redis not initialized. Call init_redis() first.")
    return redis_client


def is_redis_available() -> bool:
    """检查 Redis 是否可用"""
    return redis_client is not None


# Redis Key 前缀常量
class RedisKeyPrefix:
    """Redis键前缀常量"""

    # 认证相关
    ACCESS_TOKEN = "oauth2_access_token:"
    REFRESH_TOKEN = "oauth2_refresh_token:"
    LOGIN_USER = "login_user:"

    # 验证码
    CAPTCHA = "captcha:"

    # 用户权限缓存
    USER_PERMISSION = "user_permission:"
    USER_ROLE = "user_role:"

    # 租户相关
    TENANT = "tenant:"

    # 字典缓存
    DICT_DATA = "dict_data:"

    # 配置缓存
    CONFIG = "config:"


async def set_cache(key: str, value: str, expire: int = None) -> bool:
    """设置缓存"""
    client = await get_redis()
    if expire:
        return await client.setex(key, expire, value)
    return await client.set(key, value)


async def get_cache(key: str) -> Optional[str]:
    """获取缓存"""
    client = await get_redis()
    return await client.get(key)


async def delete_cache(key: str) -> int:
    """删除缓存"""
    client = await get_redis()
    return await client.delete(key)


async def exists_cache(key: str) -> bool:
    """检查缓存是否存在"""
    client = await get_redis()
    return await client.exists(key) > 0