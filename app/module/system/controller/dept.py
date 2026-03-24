"""
部门控制器
"""
from typing import List
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.module.system.model.user import User
from app.module.system.service.dept import DeptService
from app.module.system.schema.dept import DeptSave
from app.common.response import success

router = APIRouter()


@router.post("/create", summary="创建部门")
async def create_dept(
    req: DeptSave = Body(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:dept:create")),
):
    """创建部门"""
    dept_id = await DeptService.create(
        db, req.name, req.parent_id, req.sort, req.leader_user_id, req.phone, req.email, req.status
    )
    return success(data=dept_id)


@router.put("/update", summary="修改部门")
async def update_dept(
    req: DeptSave = Body(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:dept:update")),
):
    """更新部门"""
    if not req.id:
        return success(data=False, message="部门ID不能为空")
    await DeptService.update(
        db, req.id, req.name, req.parent_id, req.sort, req.leader_user_id, req.phone, req.email, req.status
    )
    return success(data=True)


@router.delete("/delete", summary="删除部门")
async def delete_dept(
    id: int = Query(..., description="部门ID"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:dept:delete")),
):
    """删除部门"""
    await DeptService.delete(db, id)
    return success(data=True)


@router.get("/list", summary="获取部门列表")
async def get_dept_list(
    name: str = Query(None, description="部门名称"),
    status: int = Query(None, description="状态"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:dept:query")),
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


@router.get("/simple-list", summary="获取部门精简信息列表")
async def get_simple_dept_list(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取部门精简信息列表

    只包含被开启的部门，主要用于前端的下拉选项
    需要登录认证
    """
    depts = await DeptService.get_all(db, status=0)
    return success(data=[
        {
            "id": d.id,
            "name": d.name,
            "parentId": d.parent_id,
        }
        for d in depts
    ])


@router.get("/list-all-simple", summary="获取部门精简信息列表")
async def get_list_all_simple(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取部门精简信息列表（兼容路径）"""
    depts = await DeptService.get_all(db, status=0)
    return success(data=[
        {
            "id": d.id,
            "name": d.name,
            "parentId": d.parent_id,
        }
        for d in depts
    ])


@router.get("/tree", summary="获取部门树")
async def get_dept_tree(
    name: str = Query(None, description="部门名称"),
    status: int = Query(None, description="状态"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取部门树结构"""
    tree = await DeptService.get_dept_tree(db, name, status)
    return success(data=tree)


@router.get("/get", summary="获得部门信息")
async def get_dept(
    id: int = Query(..., description="部门ID"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:dept:query")),
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