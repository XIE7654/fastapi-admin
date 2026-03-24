"""
认证服务
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.system.service.user import UserService
from app.module.system.service.menu import MenuService
from app.module.system.service.role import RoleService
from app.module.system.service.oauth2_token import OAuth2TokenService, UserTypeEnum
from app.module.system.service.login_log import LoginLogService
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
    async def login(db: AsyncSession, login_req: LoginRequest, ip: str, user_agent: str = None) -> LoginResponse:
        """
        用户登录

        Args:
            db: 数据库会话
            login_req: 登录请求
            ip: 客户端IP
            user_agent: 用户代理

        Returns:
            登录响应
        """
        # TODO: 验证验证码

        # 验证用户名密码
        user = await UserService.validate_login(db, login_req.username, login_req.password)

        # 使用 OAuth2TokenService 创建访问令牌
        access_token_do = await OAuth2TokenService.create_access_token(
            db=db,
            user_id=user.id,
            user_type=UserTypeEnum.ADMIN,
            client_id="default",
            tenant_id=login_req.tenant_id or 1,
            user=user,
        )

        # 更新最后登录信息
        user.login_ip = ip
        user.login_date = datetime.now()

        # 记录登录日志
        await LoginLogService.create_login_log(
            db=db,
            user_id=user.id,
            username=user.username,
            user_ip=ip,
            user_agent=user_agent,
            result=0,  # 成功
            tenant_id=login_req.tenant_id or 1,
        )

        return LoginResponse(
            user_id=user.id,
            access_token=access_token_do.access_token,
            refresh_token=access_token_do.refresh_token,
            expires_time=int(access_token_do.expires_time.timestamp() * 1000),
        )

    @staticmethod
    async def logout(db: AsyncSession, access_token: str, user_id: int = None, username: str = None,
                     user_ip: str = None, user_agent: str = None, tenant_id: int = None) -> bool:
        """
        用户登出

        Args:
            db: 数据库会话
            access_token: 访问令牌
            user_id: 用户ID
            username: 用户名
            user_ip: 用户IP
            user_agent: 用户代理
            tenant_id: 租户ID

        Returns:
            是否成功
        """
        result = await OAuth2TokenService.remove_access_token(db, access_token)

        # 记录登出日志
        if user_id and username:
            await LoginLogService.create_logout_log(
                db=db,
                user_id=user_id,
                username=username,
                user_ip=user_ip,
                user_agent=user_agent,
                tenant_id=tenant_id,
            )

        return result

    @staticmethod
    async def refresh_token(db: AsyncSession, refresh_token: str) -> TokenResponse:
        """
        刷新Token

        Args:
            db: 数据库会话
            refresh_token: 刷新令牌

        Returns:
            新的Token响应
        """
        access_token_do = await OAuth2TokenService.refresh_access_token(
            db=db,
            refresh_token=refresh_token,
            client_id="default",
        )

        return TokenResponse(
            access_token=access_token_do.access_token,
            refresh_token=access_token_do.refresh_token,
            token_type="Bearer",
            expires_in=int((access_token_do.expires_time - datetime.now()).total_seconds()),
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