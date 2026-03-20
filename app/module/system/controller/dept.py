"""
部门控制器
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.module.system.model.user import User
from app.module.system.service.dept import DeptService
from app.common.response import success

router = APIRouter()


@router.post("/create", summary="创建部门")
async def create_dept(
    name: str = Query(..., description="部门名称"),
    parent_id: int = Query(0, description="父部门ID"),
    sort: int = Query(0, description="显示顺序"),
    leader_user_id: int = Query(None, description="负责人用户ID"),
    phone: str = Query(None, description="联系电话"),
    email: str = Query(None, description="邮箱"),
    status: int = Query(0, description="状态"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:dept:create")),
):
    """创建部门"""
    dept_id = await DeptService.create(db, name, parent_id, sort, leader_user_id, phone, email, status)
    return success(data=dept_id)


@router.put("/update", summary="修改部门")
async def update_dept(
    id: int = Query(..., description="部门ID"),
    name: str = Query(None, description="部门名称"),
    parent_id: int = Query(None, description="父部门ID"),
    sort: int = Query(None, description="显示顺序"),
    leader_user_id: int = Query(None, description="负责人用户ID"),
    phone: str = Query(None, description="联系电话"),
    email: str = Query(None, description="邮箱"),
    status: int = Query(None, description="状态"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:dept:update")),
):
    """更新部门"""
    await DeptService.update(db, id, name, parent_id, sort, leader_user_id, phone, email, status)
    return success(data=True)


@router.delete("/delete", summary="删除部门")
async def delete_dept(
    id: int = Query(..., description="部门ID"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:dept:delete")),
):
    """删除部门"""
    await DeptService.delete(db, id)
    return success(data=True)


@router.get("/list", summary="获取部门列表")
async def get_dept_list(
    name: str = Query(None, description="部门名称"),
    status: int = Query(None, description="状态"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:dept:list")),
):
    """获取部门列表"""
    depts = await DeptService.get_all(db, name, status)
    return success(data=[
        {
            "id": d.id,
            "name": d.name,
            "parentId": d.parent_id,
            "sort": d.sort,
            "leaderUserId": d.leader_user_id,
            "phone": d.phone,
            "email": d.email,
            "status": d.status,
            "createTime": d.create_time,
        }
        for d in depts
    ])


@router.get("/tree", summary="获取部门树")
async def get_dept_tree(
    name: str = Query(None, description="部门名称"),
    status: int = Query(None, description="状态"),
    db: AsyncSession = Depends(get_db),
):
    """获取部门树结构"""
    tree = await DeptService.get_dept_tree(db, name, status)
    return success(data=tree)


@router.get("/get", summary="获得部门信息")
async def get_dept(
    id: int = Query(..., description="部门ID"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:dept:query")),
):
    """根据ID获取部门详情"""
    dept = await DeptService.get_by_id(db, id)
    if not dept:
        return success(data=None)
    return success(data={
        "id": dept.id,
        "name": dept.name,
        "parentId": dept.parent_id,
        "sort": dept.sort,
        "leaderUserId": dept.leader_user_id,
        "phone": dept.phone,
        "email": dept.email,
        "status": dept.status,
        "createTime": dept.create_time,
    })