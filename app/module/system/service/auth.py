"""
认证服务
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.system.service.user import UserService
from app.module.system.service.menu import MenuService
from app.module.system.service.role import RoleService
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.core.redis import get_redis, RedisKeyPrefix, set_cache, get_cache, delete_cache
from app.core.exceptions import BusinessException, ErrorCode
from app.module.system.schema.auth import (
    LoginRequest,
    LoginResponse,
    TokenResponse,
    PermissionInfoResponse,
)


class AuthService:
    """认证服务"""

    @staticmethod
    async def login(db: AsyncSession, login_req: LoginRequest, ip: str) -> LoginResponse:
        """
        用户登录

        Args:
            db: 数据库会话
            login_req: 登录请求
            ip: 客户端IP

        Returns:
            登录响应
        """
        # TODO: 验证验证码

        # 验证用户名密码
        user = await UserService.validate_login(db, login_req.username, login_req.password)

        # 生成Token
        access_token = create_access_token(
            subject=user.username,
            user_id=user.id,
            tenant_id=login_req.tenant_id,
        )
        refresh_token = create_refresh_token(
            subject=user.username,
            user_id=user.id,
            tenant_id=login_req.tenant_id,
        )

        # 缓存登录用户信息
        redis = await get_redis()
        await set_cache(
            f"{RedisKeyPrefix.LOGIN_USER}{user.id}",
            access_token,
            expire=30 * 24 * 60 * 60  # 30天
        )

        # 更新最后登录信息
        user.login_ip = ip
        user.login_date = datetime.now()

        return LoginResponse(
            user_id=user.id,
            username=user.username,
            nickname=user.nickname,
            avatar=user.avatar,
            dept_id=user.dept_id,
            token=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="Bearer",
                expires_in=30 * 24 * 60 * 60,
            ),
        )

    @staticmethod
    async def logout(user_id: int, token: str) -> bool:
        """
        用户登出

        Args:
            user_id: 用户ID
            token: 访问令牌

        Returns:
            是否成功
        """
        # 删除缓存的登录信息
        redis = await get_redis()
        await delete_cache(f"{RedisKeyPrefix.LOGIN_USER}{user_id}")

        # 将Token加入黑名单
        # TODO: 实现Token黑名单

        return True

    @staticmethod
    async def refresh_token(refresh_token: str) -> TokenResponse:
        """
        刷新Token

        Args:
            refresh_token: 刷新令牌

        Returns:
            新的Token响应
        """
        # 验证刷新令牌
        payload = verify_token(refresh_token, token_type="refresh")
        if not payload:
            raise BusinessException(code=ErrorCode.TOKEN_INVALID, message="刷新令牌无效")

        user_id = payload.get("user_id")
        username = payload.get("sub")
        tenant_id = payload.get("tenant_id")

        # 生成新的Token
        new_access_token = create_access_token(
            subject=username,
            user_id=user_id,
            tenant_id=tenant_id,
        )
        new_refresh_token = create_refresh_token(
            subject=username,
            user_id=user_id,
            tenant_id=tenant_id,
        )

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="Bearer",
            expires_in=30 * 24 * 60 * 60,
        )

    @staticmethod
    async def get_permission_info(db: AsyncSession, user_id: int) -> PermissionInfoResponse:
        """
        获取用户权限信息

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            权限信息响应
        """
        # 获取用户信息
        user = await UserService.get_by_id(db, user_id)
        if not user:
            raise BusinessException(code=ErrorCode.USER_NOT_EXISTS, message="用户不存在")

        # 获取用户角色
        roles = await RoleService.get_user_roles(db, user_id)
        role_codes = [r.code for r in roles]

        # 获取用户权限
        permissions = await MenuService.get_user_permissions(db, user_id)

        # 获取用户菜单
        menus = await MenuService.get_user_menus(db, user_id)

        return PermissionInfoResponse(
            user={
                "id": user.id,
                "username": user.username,
                "nickname": user.nickname,
                "avatar": user.avatar,
                "deptId": user.dept_id,
            },
            roles=role_codes,
            permissions=list(permissions),
            menus=menus,
        )

    @staticmethod
    async def validate_captcha(uuid: str, code: str) -> bool:
        """
        验证验证码

        Args:
            uuid: 验证码唯一标识
            code: 用户输入的验证码

        Returns:
            是否验证通过
        """
        redis = await get_redis()
        cached_code = await get_cache(f"{RedisKeyPrefix.CAPTCHA}{uuid}")

        if not cached_code:
            raise BusinessException(code=ErrorCode.CAPTCHA_EXPIRED, message="验证码已过期")

        if cached_code.lower() != code.lower():
            raise BusinessException(code=ErrorCode.CAPTCHA_ERROR, message="验证码错误")

        # 删除验证码
        await delete_cache(f"{RedisKeyPrefix.CAPTCHA}{uuid}")

        return True