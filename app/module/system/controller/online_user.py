"""
在线用户控制器
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.module.system.model.user import User
from app.module.system.service.online_user import OnlineUserService
from app.common.response import success

router = APIRouter()


@router.get("/list", summary="获取在线用户列表")
async def get_online_users(
    user_id: int = Query(None, description="用户ID"),
    # _: User = Depends(check_permission("system:online-user:list")),
):
    """获取在线用户列表"""
    users = await OnlineUserService.get_online_users(user_id)
    return success(data=[u.to_dict() for u in users])


@router.delete("/kick", summary="踢出用户")
async def kick_user(
    user_id: int = Query(..., description="用户ID"),
    token: str = Query(None, description="指定Token，不传则踢出所有会话"),
    # _: User = Depends(check_permission("system:online-user:kick")),
):
    """踢出在线用户"""
    count = await OnlineUserService.kick_user(user_id, token)
    return success(data={"count": count}, msg=f"已踢出 {count} 个会话")


@router.get("/tokens", summary="获取用户Token列表")
async def get_user_tokens(
    user_id: int = Query(..., description="用户ID"),
    current_user: User = Depends(get_current_user),
):
    """获取指定用户的所有Token"""
    # 只能查看自己的或超级管理员可以查看所有
    if current_user.id != 1 and current_user.id != user_id:
        return success(msg="无权限查看")

    tokens = await OnlineUserService.get_user_tokens(user_id)
    return success(data=tokens)