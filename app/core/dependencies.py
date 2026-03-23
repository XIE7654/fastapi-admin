"""
FastAPI 公共依赖
"""
from typing import Optional, List, Set, TYPE_CHECKING
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.tenant import set_tenant, get_tenant_id
from app.core.exceptions import UnauthorizedException, ForbiddenException

# 使用 TYPE_CHECKING 避免循环导入
if TYPE_CHECKING:
    from app.module.system.model.user import User

# HTTP Bearer 认证方案
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> "User":
    """
    获取当前登录用户

    Args:
        credentials: HTTP Bearer 凭证
        db: 数据库会话

    Returns:
        当前用户对象

    Raises:
        UnauthorizedException: 未授权
    """
    from app.module.system.model.user import User
    from app.module.system.service.user import UserService
    from app.module.system.service.oauth2_token import OAuth2TokenService

    if credentials is None:
        raise UnauthorizedException("请登录后访问")

    token = credentials.credentials

    # 使用 OAuth2TokenService 验证令牌
    token_data = await OAuth2TokenService.check_access_token(db, token)

    user_id = token_data.get("userId")
    tenant_id = token_data.get("tenantId")

    if user_id is None:
        raise UnauthorizedException("无效的登录凭证")

    # 设置租户上下文
    if tenant_id:
        set_tenant(tenant_id)

    # 查询用户
    user = await UserService.get_by_id(db, user_id)
    if user is None:
        raise UnauthorizedException("用户不存在")

    if user.status != 0:
        raise UnauthorizedException("用户已被禁用")

    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Optional["User"]:
    """
    获取当前登录用户（可选）

    Returns:
        当前用户对象，未登录返回None
    """
    try:
        return await get_current_user(credentials, db)
    except UnauthorizedException:
        return None


async def _get_user_permissions(db: AsyncSession, user_id: int) -> Set[str]:
    """
    获取用户权限列表

    Args:
        db: 数据库会话
        user_id: 用户ID

    Returns:
        权限标识集合
    """
    from app.module.system.service.menu import MenuService
    return await MenuService.get_user_permissions(db, user_id)


def check_permission(permission: str):
    """
    权限检查依赖

    Args:
        permission: 权限标识，如 "system:user:list"

    Returns:
        依赖函数

    Usage:
        @router.get("/users")
        async def list_users(user: User = Depends(check_permission("system:user:list"))):
            ...
    """
    async def _check_permission(
        user: "User" = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> "User":
        # 超级管理员拥有所有权限
        if user.id == 1:
            return user

        # 获取用户权限列表
        permissions = await _get_user_permissions(db, user.id)
        if permission not in permissions:
            raise ForbiddenException(f"无权限: {permission}")

        return user

    return _check_permission


def check_permissions(permissions: List[str]):
    """
    多权限检查依赖（OR关系）

    Args:
        permissions: 权限标识列表

    Returns:
        依赖函数

    Usage:
        @router.get("/users")
        async def list_users(user: User = Depends(check_permissions(["system:user:list", "system:user:query"]))):
            ...
    """
    async def _check_permissions(
        user: "User" = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> "User":
        # 超级管理员拥有所有权限
        if user.id == 1:
            return user

        # 获取用户权限列表
        user_permissions = await _get_user_permissions(db, user.id)
        if not any(p in user_permissions for p in permissions):
            raise ForbiddenException("无权限")

        return user

    return _check_permissions


def check_role(role_code: str):
    """
    角色检查依赖

    Args:
        role_code: 角色编码

    Returns:
        依赖函数
    """
    async def _check_role(
        user: "User" = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> "User":
        from app.module.system.service.role import RoleService

        # 超级管理员拥有所有角色
        if user.id == 1:
            return user

        # 获取用户角色列表
        roles = await RoleService.get_user_roles(db, user.id)
        if not any(r.code == role_code for r in roles):
            raise ForbiddenException(f"无角色权限: {role_code}")

        return user

    return _check_role