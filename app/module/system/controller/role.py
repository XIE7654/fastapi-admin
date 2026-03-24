"""
角色控制器
"""
from typing import List
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.module.system.model.user import User
from app.module.system.service.role import RoleService
from app.module.system.schema.role import RoleSave, RolePageQuery
from app.common.response import success, page_success

router = APIRouter()


@router.post("/create", summary="创建角色")
async def create_role(
    req: RoleSave = Body(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:role:create")),
):
    """创建角色"""
    role_id = await RoleService.create(
        db,
        name=req.name,
        code=req.code,
        sort=req.sort,
        data_scope=req.data_scope or 1,
        data_scope_dept_ids=req.data_scope_dept_ids,
        remark=req.remark,
    )
    return success(data=role_id)


@router.put("/update", summary="修改角色")
async def update_role(
    req: RoleSave = Body(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:role:update")),
):
    """更新角色"""
    if not req.id:
        return success(data=False, message="角色ID不能为空")
    await RoleService.update(
        db,
        role_id=req.id,
        name=req.name,
        code=req.code,
        sort=req.sort,
        data_scope=req.data_scope,
        data_scope_dept_ids=req.data_scope_dept_ids,
        remark=req.remark,
    )
    return success(data=True)


@router.delete("/delete", summary="删除角色")
async def delete_role(
    id: int = Query(..., description="角色ID"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:role:delete")),
):
    """删除角色"""
    await RoleService.delete(db, id)
    return success(data=True)


@router.delete("/delete-list", summary="批量删除角色")
async def delete_role_list(
    ids: List[int] = Query(..., description="角色ID列表"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:role:delete")),
):
    """批量删除角色"""
    await RoleService.delete_list(db, ids)
    return success(data=True)


@router.get("/get", summary="获得角色信息")
async def get_role(
    id: int = Query(..., description="角色ID"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:role:query")),
):
    """根据ID获取角色详情"""
    role = await RoleService.get_by_id(db, id)
    if not role:
        return success(data=None)
    return success(data={
        "id": role.id,
        "name": role.name,
        "code": role.code,
        "sort": role.sort,
        "dataScope": role.data_scope,
        "dataScopeDeptIds": role.data_scope_dept_ids,
        "status": role.status,
        "type": role.type,
        "remark": role.remark,
        "createTime": role.create_time,
    })


@router.get("/page", summary="获得角色分页")
async def get_role_page(
    query: RolePageQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:role:query")),
):
    """分页查询角色列表"""
    roles, total = await RoleService.get_page(db, query.page_no, query.page_size, query.name, query.code, query.status)
    return page_success(
        list_data=[
            {
                "id": r.id,
                "name": r.name,
                "code": r.code,
                "sort": r.sort,
                "dataScope": r.data_scope,
                "dataScopeDeptIds": r.data_scope_dept_ids,
                "status": r.status,
                "type": r.type,
                "remark": r.remark,
                "createTime": r.create_time,
            }
            for r in roles
        ],
        total=total,
        page_no=query.page_no,
        page_size=query.page_size,
    )


@router.get("/simple-list", summary="获取角色精简信息列表")
async def get_simple_role_list(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取角色精简信息列表（只包含被开启的角色，主要用于前端的下拉选项）"""
    roles = await RoleService.get_all(db)
    # 过滤启用的角色并按sort排序
    enabled_roles = sorted([r for r in roles if r.status == 0], key=lambda x: x.sort)
    return success(data=[
        {"id": r.id, "name": r.name, "code": r.code}
        for r in enabled_roles
    ])