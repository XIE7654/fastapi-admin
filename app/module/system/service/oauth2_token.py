"""
OAuth2 Token 服务
与 ruoyi-vue-pro 的 OAuth2TokenServiceImpl 保持一致
"""
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.system.model.oauth2 import OAuth2AccessToken, OAuth2RefreshToken, OAuth2Client
from app.core.redis import get_redis, RedisKeyPrefix, set_cache, get_cache, delete_cache
from app.core.exceptions import BusinessException, ErrorCode

logger = logging.getLogger(__name__)


# 用户类型枚举
class UserTypeEnum:
    """用户类型枚举"""
    ADMIN = 1  # 后台用户
    MEMBER = 2  # 会员用户


class OAuth2TokenService:
    """OAuth2 Token 服务"""

    # 默认客户端配置
    DEFAULT_CLIENT_ID = "default"
    DEFAULT_ACCESS_TOKEN_VALIDITY = 30 * 24 * 60 * 60  # 30天
    DEFAULT_REFRESH_TOKEN_VALIDITY = 30 * 24 * 60 * 60  # 30天

    @staticmethod
    def _generate_token() -> str:
        """生成UUID Token，与 ruoyi-vue-pro 的 IdUtil.fastSimpleUUID() 一致"""
        return uuid.uuid4().hex

    @staticmethod
    def _build_user_info(user: Any) -> str:
        """构建用户信息JSON"""
        info = {
            "nickname": user.nickname if hasattr(user, 'nickname') else "",
            "deptId": str(user.dept_id) if hasattr(user, 'dept_id') and user.dept_id else None,
        }
        return json.dumps(info, ensure_ascii=False)

    @staticmethod
    async def get_client_by_id(db: AsyncSession, client_id: str) -> Optional[OAuth2Client]:
        """获取OAuth2客户端"""
        result = await db.execute(
            select(OAuth2Client).where(
                OAuth2Client.client_id == client_id,
                OAuth2Client.deleted == 0
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_access_token(
        db: AsyncSession,
        user_id: int,
        user_type: int = UserTypeEnum.ADMIN,
        client_id: str = DEFAULT_CLIENT_ID,
        scopes: List[str] = None,
        tenant_id: int = 1,
        user: Any = None,
    ) -> OAuth2AccessToken:
        """
        创建访问令牌

        与 ruoyi-vue-pro 的 createAccessToken 方法一致
        """
        # 获取客户端配置
        client = await OAuth2TokenService.get_client_by_id(db, client_id)
        if client:
            access_token_validity = client.access_token_validity_seconds
            refresh_token_validity = client.refresh_token_validity_seconds
        else:
            access_token_validity = OAuth2TokenService.DEFAULT_ACCESS_TOKEN_VALIDITY
            refresh_token_validity = OAuth2TokenService.DEFAULT_REFRESH_TOKEN_VALIDITY

        # 生成刷新令牌
        refresh_token = OAuth2TokenService._generate_token()
        refresh_token_do = OAuth2RefreshToken(
            user_id=user_id,
            user_type=user_type,
            refresh_token=refresh_token,
            client_id=client_id,
            scopes=json.dumps(scopes) if scopes else None,
            expires_time=datetime.now() + timedelta(seconds=refresh_token_validity),
            tenant_id=tenant_id,
        )
        db.add(refresh_token_do)

        # 生成访问令牌
        access_token = OAuth2TokenService._generate_token()
        access_token_do = OAuth2AccessToken(
            user_id=user_id,
            user_type=user_type,
            user_info=OAuth2TokenService._build_user_info(user) if user else "{}",
            access_token=access_token,
            refresh_token=refresh_token,
            client_id=client_id,
            scopes=json.dumps(scopes) if scopes else None,
            expires_time=datetime.now() + timedelta(seconds=access_token_validity),
            tenant_id=tenant_id,
        )
        db.add(access_token_do)
        await db.flush()

        # 解析 user_info 为字典（存储时是JSON字符串）
        user_info_dict = {}
        if access_token_do.user_info:
            if isinstance(access_token_do.user_info, str):
                try:
                    user_info_dict = json.loads(access_token_do.user_info)
                except (json.JSONDecodeError, TypeError):
                    user_info_dict = {}
            elif isinstance(access_token_do.user_info, dict):
                user_info_dict = access_token_do.user_info

        # 缓存到 Redis（失败不影响主流程）
        token_data = {
            "id": access_token_do.id,
            "userId": user_id,
            "userType": user_type,
            "userInfo": user_info_dict,
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "clientId": client_id,
            "scopes": scopes,
            "expiresTime": access_token_do.expires_time.isoformat(),
            "tenantId": tenant_id,
        }
        try:
            redis = await get_redis()
            await redis.set(
                f"{RedisKeyPrefix.ACCESS_TOKEN}{access_token}",
                json.dumps(token_data, ensure_ascii=False),
                ex=access_token_validity
            )
            logger.debug(f"Token已缓存到Redis: {access_token[:8]}..., userId={user_id}, tenantId={tenant_id}")
        except Exception as e:
            logger.warning(f"Redis 缓存 token 失败: {e}")

        return access_token_do

    @staticmethod
    async def get_access_token(db: AsyncSession, access_token: str) -> Optional[Dict[str, Any]]:
        """
        获取访问令牌信息

        优先从Redis获取，其次从数据库获取
        """
        # 优先从 Redis 获取
        try:
            redis = await get_redis()
            cached = await redis.get(f"{RedisKeyPrefix.ACCESS_TOKEN}{access_token}")
            if cached:
                logger.debug(f"从Redis获取token成功: {access_token[:8]}...")
                return json.loads(cached)
            else:
                logger.debug(f"Redis中没有找到token: {access_token[:8]}...")
        except Exception as e:
            logger.warning(f"Redis 获取 token 失败，降级到数据库查询: {e}")

        # 从数据库获取
        logger.debug(f"从数据库查询token: {access_token[:8]}...")
        result = await db.execute(
            select(OAuth2AccessToken).where(
                OAuth2AccessToken.access_token == access_token,
                OAuth2AccessToken.deleted == 0
            )
        )
        token_do = result.scalar_one_or_none()
        if not token_do:
            logger.warning(f"数据库中没有找到token: {access_token[:8]}...")
            return None

        # 检查是否过期
        if token_do.expires_time and datetime.now() > token_do.expires_time:
            logger.warning(f"Token已过期: {access_token[:8]}..., 过期时间: {token_do.expires_time}")
            return None

        logger.debug(f"从数据库获取token成功: userId={token_do.user_id}, tenantId={token_do.tenant_id}")

        # 解析 user_info 和 scopes 字段（数据库中存储为JSON字符串）
        user_info = token_do.user_info
        if isinstance(user_info, str):
            try:
                user_info = json.loads(user_info)
            except (json.JSONDecodeError, TypeError):
                user_info = {}

        scopes = None
        if token_do.scopes:
            if isinstance(token_do.scopes, str):
                try:
                    scopes = json.loads(token_do.scopes)
                except (json.JSONDecodeError, TypeError):
                    scopes = None
            elif isinstance(token_do.scopes, list):
                scopes = token_do.scopes

        # 缓存到 Redis（失败不影响主流程）
        token_data = {
            "id": token_do.id,
            "userId": token_do.user_id,
            "userType": token_do.user_type,
            "userInfo": user_info,
            "accessToken": token_do.access_token,
            "refreshToken": token_do.refresh_token,
            "clientId": token_do.client_id,
            "scopes": scopes,
            "expiresTime": token_do.expires_time.isoformat() if token_do.expires_time else None,
            "tenantId": token_do.tenant_id,
        }
        remaining_seconds = int((token_do.expires_time - datetime.now()).total_seconds())
        if remaining_seconds > 0:
            try:
                redis = await get_redis()
                await redis.set(
                    f"{RedisKeyPrefix.ACCESS_TOKEN}{access_token}",
                    json.dumps(token_data, ensure_ascii=False),
                    ex=remaining_seconds
                )
            except Exception as e:
                logger.warning(f"Redis 缓存 token 失败: {e}")

        return token_data

    @staticmethod
    async def check_access_token(db: AsyncSession, access_token: str) -> Dict[str, Any]:
        """
        检查访问令牌有效性

        :raises BusinessException: 令牌无效或已过期
        """
        token_data = await OAuth2TokenService.get_access_token(db, access_token)
        if not token_data:
            raise BusinessException(code=ErrorCode.TOKEN_INVALID, message="访问令牌不存在")

        expires_time = datetime.fromisoformat(token_data["expiresTime"]) if token_data.get("expiresTime") else None
        if expires_time and datetime.now() > expires_time:
            raise BusinessException(code=ErrorCode.TOKEN_EXPIRED, message="访问令牌已过期")

        return token_data

    @staticmethod
    async def remove_access_token(db: AsyncSession, access_token: str) -> bool:
        """
        移除访问令牌（登出）
        """
        # 从数据库删除
        result = await db.execute(
            select(OAuth2AccessToken).where(
                OAuth2AccessToken.access_token == access_token,
                OAuth2AccessToken.deleted == 0
            )
        )
        token_do = result.scalar_one_or_none()
        if token_do:
            # 软删除
            token_do.deleted = 1
            await db.flush()

            # 删除刷新令牌
            await db.execute(
                delete(OAuth2RefreshToken).where(
                    OAuth2RefreshToken.refresh_token == token_do.refresh_token
                )
            )

        # 从 Redis 删除（失败不影响主流程）
        try:
            redis = await get_redis()
            await redis.delete(f"{RedisKeyPrefix.ACCESS_TOKEN}{access_token}")
        except Exception as e:
            logger.warning(f"Redis 删除 token 失败: {e}")

        return True

    @staticmethod
    async def refresh_access_token(
        db: AsyncSession,
        refresh_token: str,
        client_id: str = DEFAULT_CLIENT_ID,
    ) -> OAuth2AccessToken:
        """
        刷新访问令牌

        与 ruoyi-vue-pro 的 refreshAccessToken 方法一致
        """
        # 查询刷新令牌
        result = await db.execute(
            select(OAuth2RefreshToken).where(
                OAuth2RefreshToken.refresh_token == refresh_token,
                OAuth2RefreshToken.deleted == 0
            )
        )
        refresh_token_do = result.scalar_one_or_none()

        if not refresh_token_do:
            raise BusinessException(code=ErrorCode.TOKEN_INVALID, message="无效的刷新令牌")

        if refresh_token_do.client_id != client_id:
            raise BusinessException(code=ErrorCode.TOKEN_INVALID, message="刷新令牌的客户端编号不正确")

        # 检查是否过期
        if refresh_token_do.expires_time and datetime.now() > refresh_token_do.expires_time:
            raise BusinessException(code=ErrorCode.TOKEN_EXPIRED, message="刷新令牌已过期")

        # 删除旧的访问令牌
        await db.execute(
            delete(OAuth2AccessToken).where(
                OAuth2AccessToken.refresh_token == refresh_token
            )
        )

        # 获取客户端配置
        client = await OAuth2TokenService.get_client_by_id(db, client_id)
        if client:
            access_token_validity = client.access_token_validity_seconds
        else:
            access_token_validity = OAuth2TokenService.DEFAULT_ACCESS_TOKEN_VALIDITY

        # 生成新的访问令牌
        new_access_token = OAuth2TokenService._generate_token()
        access_token_do = OAuth2AccessToken(
            user_id=refresh_token_do.user_id,
            user_type=refresh_token_do.user_type,
            user_info="{}",
            access_token=new_access_token,
            refresh_token=refresh_token,
            client_id=client_id,
            scopes=refresh_token_do.scopes,
            expires_time=datetime.now() + timedelta(seconds=access_token_validity),
            tenant_id=refresh_token_do.tenant_id,
        )
        db.add(access_token_do)
        await db.flush()

        # 缓存到 Redis（失败不影响主流程）
        # 解析 scopes 字段
        scopes = None
        if access_token_do.scopes:
            if isinstance(access_token_do.scopes, str):
                try:
                    scopes = json.loads(access_token_do.scopes)
                except (json.JSONDecodeError, TypeError):
                    scopes = None
            elif isinstance(access_token_do.scopes, list):
                scopes = access_token_do.scopes

        # 解析 user_info 字段
        user_info = access_token_do.user_info
        if isinstance(user_info, str):
            try:
                user_info = json.loads(user_info)
            except (json.JSONDecodeError, TypeError):
                user_info = {}

        token_data = {
            "id": access_token_do.id,
            "userId": access_token_do.user_id,
            "userType": access_token_do.user_type,
            "userInfo": user_info,
            "accessToken": new_access_token,
            "refreshToken": refresh_token,
            "clientId": client_id,
            "scopes": scopes,
            "expiresTime": access_token_do.expires_time.isoformat(),
            "tenantId": access_token_do.tenant_id,
        }
        try:
            redis = await get_redis()
            await redis.set(
                f"{RedisKeyPrefix.ACCESS_TOKEN}{new_access_token}",
                json.dumps(token_data, ensure_ascii=False),
                ex=access_token_validity
            )
        except Exception as e:
            logger.warning(f"Redis 缓存 token 失败: {e}")

        return access_token_do