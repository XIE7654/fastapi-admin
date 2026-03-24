"""
认证控制器
"""
from typing import Optional
from fastapi import APIRouter, Depends, Request, Body, Header, Query
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
    # 获取 User-Agent
    user_agent = request.headers.get("user-agent", "")

    result = await AuthService.login(db, login_req, ip, user_agent)
    return success(data=result)


@router.post("/logout", summary="登出系统")
async def logout(
    request: Request,
    db: AsyncSession = Depends(get_db),
    authorization: Optional[str] = Header(None),
    current_user: User = Depends(get_current_user),
):
    """用户登出"""
    # 从 Authorization header 提取 token
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]

    if token:
        # 获取客户端信息
        ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")

        await AuthService.logout(
            db=db,
            access_token=token,
            user_id=current_user.id,
            username=current_user.username,
            user_ip=ip,
            user_agent=user_agent,
            tenant_id=current_user.tenant_id,
        )
    return success(data=True)


@router.post("/refresh-token", summary="刷新令牌")
async def refresh_token(
    refresh_token: str = Query(..., alias="refreshToken", description="刷新令牌"),
    db: AsyncSession = Depends(get_db),
):
    """
    刷新Token

    - **refreshToken**: 刷新令牌（Query参数）
    """
    access_token_do = await AuthService.refresh_token(db, refresh_token)

    # 与 Java 版本的 AuthLoginRespVO 保持一致
    return success(data={
        "userId": access_token_do.user_id,
        "accessToken": access_token_do.access_token,
        "refreshToken": access_token_do.refresh_token,
        "expiresTime": int(access_token_do.expires_time.timestamp() * 1000),
    })


@router.get("/get-permission-info", summary="获取登录用户的权限信息")
async def get_permission_info(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户的权限信息，包括角色、权限标识和菜单"""
    result = await AuthService.get_permission_info(db, current_user.id)
    return success(data=result)