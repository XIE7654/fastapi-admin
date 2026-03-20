"""
FastAPI 公共依赖
"""
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_token
from app.core.tenant import set_tenant, get_tenant_id
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.module.system.model.user import User
from app.module.system.service.user import UserService

# HTTP Bearer 认证方案
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
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
    if credentials is None:
        raise UnauthorizedException("请登录后访问")

    token = credentials.credentials

    # 验证令牌
    payload = verify_token(token, token_type="access")
    if payload is None:
        raise UnauthorizedException("登录已过期，请重新登录")

    user_id = payload.get("user_id")
    tenant_id = payload.get("tenant_id")

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
) -> Optional[User]:
    """
    获取当前登录用户（可选）

    Returns:
        当前用户对象，未登录返回None
    """
    try:
        return await get_current_user(credentials, db)
    except UnauthorizedException:
        return None


def check_permission(permission: str):
    """
    权限检查依赖

    Args:
        permission: 权限标识，如 "system:user:list"

    Returns:
        依赖函数

    Usage:
        @router.get("/users", dependencies=[Depends(check_permission("system:user:list"))])
    """
    async def _check_permission(user: User = Depends(get_current_user)) -> User:
        # TODO: 实现权限检查逻辑
        # 从缓存或数据库获取用户权限列表
        # if permission not in user.permissions:
        #     raise ForbiddenException(f"无权限: {permission}")
        return user

    return _check_permission


def check_permissions(permissions: List[str]):
    """
    多权限检查依赖（OR关系）

    Args:
        permissions: 权限标识列表

    Returns:
        依赖函数
    """
    async def _check_permissions(user: User = Depends(get_current_user)) -> User:
        # TODO: 实现权限检查逻辑
        # user_permissions = await get_user_permissions(user.id)
        # if not any(p in user_permissions for p in permissions):
        #     raise ForbiddenException("无权限")
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
    async def _check_role(user: User = Depends(get_current_user)) -> User:
        # TODO: 实现角色检查逻辑
        return user

    return _check_role