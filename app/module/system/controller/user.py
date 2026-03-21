"""
用户控制器
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.module.system.model.user import User
from app.module.system.service.user import UserService
from app.module.system.schema.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserPageQuery,
    UserPasswordUpdate,
    UserResetPassword,
)
from app.common.response import success, error, page_success

router = APIRouter()


@router.post("/create", summary="新增用户")
async def create_user(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:user:create")),
):
    """创建新用户"""
    user_id = await UserService.create(db, user_create)
    return success(data=user_id)


@router.put("/update", summary="修改用户")
async def update_user(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:user:update")),
):
    """更新用户信息"""
    await UserService.update(db, user_update)
    return success(data=True)


@router.delete("/delete", summary="删除用户")
async def delete_user(
    id: int = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:user:delete")),
):
    """删除用户"""
    await UserService.delete(db, id)
    return success(data=True)


@router.delete("/delete-list", summary="批量删除用户")
async def delete_user_list(
    ids: List[int] = Query(..., description="用户ID列表"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:user:delete")),
):
    """批量删除用户"""
    await UserService.delete_list(db, ids)
    return success(data=True)


@router.put("/update-password", summary="重置用户密码")
async def update_user_password(
    req: UserResetPassword,
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:user:update-password")),
):
    """重置用户密码（管理员操作）"""
    await UserService.reset_password(db, req.id, req.password)
    return success(data=True)


@router.put("/update-status", summary="修改用户状态")
async def update_user_status(
    id: int = Query(..., description="用户ID"),
    status: int = Query(..., ge=0, le=1, description="状态"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:user:update")),
):
    """更新用户状态（启用/禁用）"""
    await UserService.update_status(db, id, status)
    return success(data=True)


@router.get("/page", summary="获得用户分页列表")
async def get_user_page(
    query: UserPageQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:user:query")),
):
    """分页查询用户列表"""
    users, total = await UserService.get_list(db, query)
    return page_success(
        list_data=[UserResponse.model_validate(u) for u in users],
        total=total,
        page_no=query.page_no,
        page_size=query.page_size,
    )


@router.get("/simple-list", summary="获取用户精简信息列表")
async def get_simple_user_list(
    db: AsyncSession = Depends(get_db),
):
    """获取用户精简信息列表（只包含被开启的用户，主要用于前端的下拉选项）"""
    users = await UserService.get_enabled_users(db)
    return success(data=[
        {
            "id": u.id,
            "username": u.username,
            "nickname": u.nickname,
            "deptId": u.dept_id,
        }
        for u in users
    ])


@router.get("/get", summary="获得用户详情")
async def get_user(
    id: int = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db),
):
    """根据ID获取用户详情"""
    user = await UserService.get_by_id(db, id)
    if not user:
        return success(data=None)
    return success(data=UserResponse.model_validate(user))