"""
权限控制器
"""
from typing import Set, List
from fastapi import APIRouter, Depends, Query, Body
from pydantic import Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import check_permission
from app.module.system.model.user import User
from app.module.system.service.permission import PermissionService
from app.common.response import success
from app.common.schema import CamelModel

router = APIRouter()


class AssignUserRoleReq(CamelModel):
    """分配用户角色请求"""

    user_id: int = Field(..., description="用户ID")
    role_ids: List[int] = Field(default_factory=list, description="角色ID列表")


@router.get("/list-user-roles", summary="获得管理员拥有的角色编号列表")
async def list_user_roles(
    userId: int = Query(..., alias="userId", description="用户编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:permission:assign-user-role")),
):
    """
    获得管理员拥有的角色编号列表

    Args:
        userId: 用户ID
        db: 数据库会话

    Returns:
        角色ID列表
    """
    role_ids = await PermissionService.get_user_role_id_list(db, userId)
    return success(data=list(role_ids))


@router.get("/list-role-menus", summary="获得角色拥有的菜单编号")
async def list_role_menus(
    roleId: int = Query(..., alias="roleId", description="角色编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:permission:assign-role-menu")),
):
    """
    获得角色拥有的菜单编号

    Args:
        roleId: 角色ID
        db: 数据库会话

    Returns:
        菜单ID列表
    """
    menu_ids = await PermissionService.get_role_menu_id_list(db, roleId)
    return success(data=list(menu_ids))


@router.post("/assign-user-role", summary="分配用户角色")
async def assign_user_role(
    req: AssignUserRoleReq = Body(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:permission:assign-user-role")),
):
    """
    分配用户角色

    Args:
        req: 请求参数
        db: 数据库会话

    Returns:
        是否成功
    """
    await PermissionService.assign_user_roles(db, req.user_id, set(req.role_ids))
    await db.commit()
    return success(data=True)