"""
用户控制器
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.module.system.model.user import User
from app.module.system.model.dept import Dept
from app.module.system.service.user import UserService
from app.module.system.service.dept import DeptService
from app.module.system.schema.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserPageQuery,
    UserPasswordUpdate,
    UserResetPassword,
    UserUpdateStatus,
)
from app.common.response import success, error, page_success

router = APIRouter()


@router.post("/create", summary="新增用户")
async def create_user(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:user:create")),
):
    """创建新用户"""
    user_id = await UserService.create(db, user_create)
    return success(data=user_id)


@router.put("/update", summary="修改用户")
async def update_user(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:user:update")),
):
    """更新用户信息"""
    await UserService.update(db, user_update.id, user_update)
    return success(data=True)


@router.delete("/delete", summary="删除用户")
async def delete_user(
    id: int = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:user:delete")),
):
    """删除用户"""
    await UserService.delete(db, id)
    return success(data=True)


@router.delete("/delete-list", summary="批量删除用户")
async def delete_user_list(
    ids: List[int] = Query(..., description="用户ID列表"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:user:delete")),
):
    """批量删除用户"""
    await UserService.delete_list(db, ids)
    return success(data=True)


@router.put("/update-password", summary="重置用户密码")
async def update_user_password(
    req: UserResetPassword,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:user:update-password")),
):
    """重置用户密码（管理员操作）"""
    await UserService.reset_password(db, req.id, req.password)
    return success(data=True)


@router.put("/update-status", summary="修改用户状态")
async def update_user_status(
    req: UserUpdateStatus,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:user:update")),
):
    """更新用户状态（启用/禁用）"""
    await UserService.update_status(db, req.id, req.status)
    return success(data=True)


@router.get("/page", summary="获得用户分页列表")
async def get_user_page(
    query: UserPageQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:user:query")),
):
    """分页查询用户列表"""
    users, total = await UserService.get_list(db, query)

    # 批量获取部门名称
    dept_ids = [u.dept_id for u in users if u.dept_id]
    dept_map = {}
    if dept_ids:
        from sqlalchemy import select
        result = await db.execute(
            select(Dept.id, Dept.name).where(Dept.id.in_(dept_ids), Dept.deleted == 0)
        )
        dept_map = {row.id: row.name for row in result.all()}

    # 构建响应数据，添加部门名称
    user_responses = []
    for u in users:
        user_dict = {
            "id": u.id,
            "username": u.username,
            "nickname": u.nickname,
            "email": u.email,
            "mobile": u.mobile,
            "gender": u.gender,
            "dept_id": u.dept_id,
            "dept_name": dept_map.get(u.dept_id) if u.dept_id else None,
            "post_ids": u.post_ids,
            "status": u.status,
            "remark": u.remark,
            "avatar": u.avatar,
            "login_ip": u.login_ip,
            "login_date": u.login_date,
            "create_time": u.create_time,
        }
        user_responses.append(UserResponse.model_validate(user_dict))

    return page_success(
        list_data=user_responses,
        total=total,
        page_no=query.page_no,
        page_size=query.page_size,
    )


@router.get("/simple-list", summary="获取用户精简信息列表")
async def get_simple_user_list(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
    _: User = Depends(check_permission("system:user:query")),
):
    """根据ID获取用户详情"""
    user = await UserService.get_by_id(db, id)
    if not user:
        return success(data=None)
    return success(data=UserResponse.model_validate(user))