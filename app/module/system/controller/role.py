"""
角色控制器
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.module.system.model.user import User
from app.module.system.service.role import RoleService
from app.module.system.schema.role import RoleSave, RolePageQuery
from app.common.response import success, page_success
from app.common.excel import ExcelUtils

router = APIRouter()

# 状态字典
STATUS_DICT = {0: "开启", 1: "禁用"}

# 角色类型字典
ROLE_TYPE_DICT = {1: "系统内置", 2: "自定义"}

# 数据权限字典
DATA_SCOPE_DICT = {1: "全部数据权限", 2: "指定部门数据权限", 3: "本部门数据权限", 4: "本部门及以下数据权限", 5: "仅本人数据权限"}


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


@router.get("/export-excel", summary="导出角色 Excel")
async def export_role_excel(
    name: Optional[str] = Query(None, description="角色名称"),
    code: Optional[str] = Query(None, description="角色编码"),
    status: Optional[int] = Query(None, ge=0, le=1, description="状态"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:role:export")),
):
    """导出角色 Excel"""
    # 获取数据
    roles = await RoleService.get_list(db, name=name, code=code, status=status)

    # 定义表头和字段
    headers = ["角色编号", "角色名称", "角色编码", "显示顺序", "数据范围", "数据范围部门编号", "状态", "角色类型", "备注", "创建时间"]
    fields = ["id", "name", "code", "sort", "data_scope", "data_scope_dept_ids", "status", "type", "remark", "create_time"]

    # 定义转换器
    converters = {
        "status": lambda v: STATUS_DICT.get(v, v),
        "type": lambda v: ROLE_TYPE_DICT.get(v, v),
        "data_scope": lambda v: DATA_SCOPE_DICT.get(v, v),
    }

    # 导出 Excel
    return ExcelUtils.export_excel(
        data=roles,
        headers=headers,
        fields=fields,
        filename="角色数据.xlsx",
        sheet_name="角色列表",
        converters=converters,
    )