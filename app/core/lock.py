"""
分布式锁服务
基于Redis实现
"""
import time
import uuid
from typing import Optional
from contextlib import asynccontextmanager

from app.core.redis import get_redis


class DistributedLock:
    """分布式锁"""

    def __init__(
        self,
        key: str,
        timeout: int = 30,
        retry_times: int = 3,
        retry_delay: float = 0.1,
    ):
        """
        初始化分布式锁

        Args:
            key: 锁的键名
            timeout: 锁超时时间（秒）
            retry_times: 获取锁重试次数
            retry_delay: 重试间隔（秒）
        """
        self.key = f"lock:{key}"
        self.timeout = timeout
        self.retry_times = retry_times
        self.retry_delay = retry_delay
        self.identifier = str(uuid.uuid4())
        self._acquired = False

    async def acquire(self) -> bool:
        """
        获取锁

        Returns:
            是否成功获取锁
        """
        redis = await get_redis()

        for _ in range(self.retry_times):
            # 使用SET NX EX原子操作
            result = await redis.set(
                self.key,
                self.identifier,
                nx=True,
                ex=self.timeout
            )
            if result:
                self._acquired = True
                return True

            # 等待重试
            time.sleep(self.retry_delay)

        return False

    async def release(self) -> bool:
        """
        释放锁

        Returns:
            是否成功释放锁
        """
        if not self._acquired:
            return False

        redis = await get_redis()

        # 使用Lua脚本确保原子性：只有锁的持有者才能释放锁
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """

        result = await redis.eval(lua_script, 1, self.key, self.identifier)
        self._acquired = False

        return result == 1

    @asynccontextmanager
    async def __aenter__(self):
        """上下文管理器入口"""
        acquired = await self.acquire()
        if not acquired:
            raise RuntimeError(f"Failed to acquire lock: {self.key}")
        try:
            yield self
        finally:
            await self.release()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        await self.release()


@asynccontextmanager
async def distributed_lock(
    key: str,
    timeout: int = 30,
    retry_times: int = 3,
):
    """
    分布式锁上下文管理器

    Args:
        key: 锁的键名
        timeout: 锁超时时间（秒）
        retry_times: 获取锁重试次数

    Usage:
        async with distributed_lock("user:1:update"):
            # 执行需要加锁的操作
            ...
    """
    lock = DistributedLock(key, timeout, retry_times)
    async with lock:
        yield lock


async def try_lock(key: str, timeout: int = 30) -> Optional[DistributedLock]:
    """
    尝试获取锁（非阻塞）

    Args:
        key: 锁的键名
        timeout: 锁超时时间（秒）

    Returns:
        成功返回锁对象，失败返回None

    Usage:
        lock = await try_lock("resource")
        if lock:
            try:
                # 执行操作
                ...
            finally:
                await lock.release()
    """
    lock = DistributedLock(key, timeout, retry_times=1)
    if await lock.acquire():
        return lock
    return None


class Lock4j:
    """
    分布式锁注解式用法（类似Java的Lock4j）

    Usage:
        @Lock4j(key="user:{user_id}", timeout=30)
        async def update_user(user_id: int, ...):
            ...
    """

    def __init__(
        self,
        key: str,
        timeout: int = 30,
        retry_times: int = 3,
    ):
        self.key = key
        self.timeout = timeout
        self.retry_times = retry_times

    def __call__(self, func):
        import asyncio
        from functools import wraps

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 格式化key
            lock_key = self.key.format(*args, **kwargs)

            async with distributed_lock(lock_key, self.timeout, self.retry_times):
                return await func(*args, **kwargs)

        return wrapper