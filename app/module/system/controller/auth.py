"""
认证控制器
"""
from typing import Optional
from fastapi import APIRouter, Depends, Request, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.module.system.model.user import User
from app.module.system.service.auth import AuthService
from app.module.system.schema.auth import (
    LoginRequest,
    LoginResponse,
    TokenResponse,
    RefreshTokenRequest,
    PermissionInfoResponse,
)
from app.common.response import success, error

router = APIRouter()


@router.post("/login", summary="使用账号密码登录")
async def login(
    request: Request,
    login_req: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    用户登录

    - **username**: 用户账号
    - **password**: 密码
    - **captcha**: 验证码（可选）
    - **uuid**: 验证码标识（可选）
    """
    # 获取客户端IP
    ip = request.client.host if request.client else "unknown"

    result = await AuthService.login(db, login_req, ip)
    return success(data=result)


@router.post("/logout", summary="登出系统")
async def logout(
    current_user: User = Depends(get_current_user),
):
    """用户登出"""
    await AuthService.logout(current_user.id, "")
    return success(data=True)


@router.post("/refresh-token", summary="刷新令牌")
async def refresh_token(
    req: RefreshTokenRequest,
):
    """
    刷新Token

    - **refresh_token**: 刷新令牌
    """
    result = await AuthService.refresh_token(req.refresh_token)
    return success(data=result)


@router.get("/get-permission-info", summary="获取登录用户的权限信息")
async def get_permission_info(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户的权限信息，包括角色、权限标识和菜单"""
    result = await AuthService.get_permission_info(db, current_user.id)
    return success(data=result)