"""
在线用户服务
"""
from typing import List, Optional
from datetime import datetime, timedelta
import json

from app.core.redis import get_redis, RedisKeyPrefix, get_cache, set_cache, delete_cache
from app.module.system.model.online_user import OnlineUser


class OnlineUserService:
    """在线用户服务"""

    # Token过期时间（秒）
    TOKEN_TIMEOUT = 30 * 24 * 60 * 60  # 30天

    @staticmethod
    def _get_token_key(token: str) -> str:
        """获取Token缓存键"""
        return f"{RedisKeyPrefix.ACCESS_TOKEN}{token}"

    @staticmethod
    def _get_user_tokens_key(user_id: int) -> str:
        """获取用户Token列表缓存键"""
        return f"user_tokens:{user_id}"

    @staticmethod
    async def add_online_user(
        user_id: int,
        username: str,
        nickname: str,
        token: str,
        user_ip: str = None,
        user_agent: str = None,
        browser: str = None,
        os: str = None,
        dept_id: int = None,
        dept_name: str = None,
        tenant_id: int = None,
    ) -> None:
        """添加在线用户"""
        online_user = OnlineUser(
            user_id=user_id,
            username=username,
            nickname=nickname,
            token=token,
            user_ip=user_ip,
            user_agent=user_agent,
            browser=browser,
            os=os,
            dept_id=dept_id,
            dept_name=dept_name,
            login_time=datetime.now(),
            session_timeout=datetime.now() + timedelta(seconds=OnlineUserService.TOKEN_TIMEOUT),
            tenant_id=tenant_id,
        )

        # 存储Token到用户映射
        await set_cache(
            OnlineUserService._get_token_key(token),
            json.dumps(online_user.to_dict()),
            expire=OnlineUserService.TOKEN_TIMEOUT
        )

        # 将Token添加到用户的Token列表
        redis = await get_redis()
        await redis.sadd(
            OnlineUserService._get_user_tokens_key(user_id),
            token
        )

    @staticmethod
    async def get_online_user(token: str) -> Optional[OnlineUser]:
        """根据Token获取在线用户"""
        data = await get_cache(OnlineUserService._get_token_key(token))
        if not data:
            return None

        return OnlineUser.from_dict(json.loads(data))

    @staticmethod
    async def remove_online_user(token: str) -> bool:
        """移除在线用户"""
        online_user = await OnlineUserService.get_online_user(token)
        if not online_user:
            return False

        # 删除Token映射
        await delete_cache(OnlineUserService._get_token_key(token))

        # 从用户Token列表中移除
        redis = await get_redis()
        await redis.srem(
            OnlineUserService._get_user_tokens_key(online_user.user_id),
            token
        )

        return True

    @staticmethod
    async def get_user_tokens(user_id: int) -> List[str]:
        """获取用户的所有Token"""
        redis = await get_redis()
        tokens = await redis.smembers(OnlineUserService._get_user_tokens_key(user_id))
        return list(tokens) if tokens else []

    @staticmethod
    async def get_online_users(user_id: int = None) -> List[OnlineUser]:
        """获取在线用户列表"""
        if user_id:
            tokens = await OnlineUserService.get_user_tokens(user_id)
        else:
            # 获取所有在线用户（生产环境应使用SCAN命令）
            redis = await get_redis()
            pattern = f"{RedisKeyPrefix.ACCESS_TOKEN}*"
            keys = []
            async for key in redis.scan_iter(match=pattern):
                keys.append(key)
            tokens = [k.replace(RedisKeyPrefix.ACCESS_TOKEN, "") for k in keys]

        users = []
        for token in tokens:
            user = await OnlineUserService.get_online_user(token)
            if user:
                users.append(user)

        return users

    @staticmethod
    async def kick_user(user_id: int, token: str = None) -> int:
        """踢出用户（可选踢出指定Token或全部）"""
        if token:
            await OnlineUserService.remove_online_user(token)
            return 1

        # 踢出用户所有会话
        tokens = await OnlineUserService.get_user_tokens(user_id)
        count = 0
        for t in tokens:
            if await OnlineUserService.remove_online_user(t):
                count += 1

        return count

    @staticmethod
    async def refresh_token_timeout(token: str) -> bool:
        """刷新Token超时时间"""
        online_user = await OnlineUserService.get_online_user(token)
        if not online_user:
            return False

        # 更新超时时间并刷新缓存
        online_user.session_timeout = datetime.now() + timedelta(seconds=OnlineUserService.TOKEN_TIMEOUT)
        await set_cache(
            OnlineUserService._get_token_key(token),
            json.dumps(online_user.to_dict()),
            expire=OnlineUserService.TOKEN_TIMEOUT
        )

        return True