"""
租户套餐控制器
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.module.system.model.user import User
from app.module.system.service.tenant_package import TenantPackageService
from app.common.response import success, page_success

router = APIRouter()


@router.get("/get-simple-list", summary="获取租户套餐精简信息列表")
async def get_tenant_package_simple_list(
    db: AsyncSession = Depends(get_db),
):
    """
    获取租户套餐精简信息列表

    只包含被开启的租户套餐，主要用于前端的下拉选项
    无需权限认证
    """
    packages = await TenantPackageService.get_list_by_status(db, status=0)
    return success(data=[
        {
            "id": p.id,
            "name": p.name,
        }
        for p in packages
    ])


@router.get("/simple-list", summary="获取租户套餐精简信息列表")
async def get_simple_list(
    db: AsyncSession = Depends(get_db),
):
    """获取租户套餐精简信息列表（兼容路径）"""
    packages = await TenantPackageService.get_list_by_status(db, status=0)
    return success(data=[
        {
            "id": p.id,
            "name": p.name,
        }
        for p in packages
    ])


@router.get("/page", summary="获得租户套餐分页")
async def get_tenant_package_page(
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    name: str = Query(None, description="套餐名称"),
    status: int = Query(None, description="状态"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:tenant-package:query")),
):
    """分页查询租户套餐列表"""
    packages, total = await TenantPackageService.get_page(db, page_no, page_size, name, status)
    return page_success(
        list_data=[
            {
                "id": p.id,
                "name": p.name,
                "status": p.status,
                "remark": p.remark,
                "menuIds": p.menu_ids,
                "createTime": p.create_time,
            }
            for p in packages
        ],
        total=total,
        page_no=page_no,
        page_size=page_size,
    )


@router.get("/get", summary="获得租户套餐")
async def get_tenant_package(
    id: int = Query(..., description="套餐编号"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:tenant-package:query")),
):
    """根据ID获取租户套餐详情"""
    package = await TenantPackageService.get_by_id(db, id)
    if not package:
        return success(data=None)
    return success(data={
        "id": package.id,
        "name": package.name,
        "status": package.status,
        "remark": package.remark,
        "menuIds": package.menu_ids,
        "createTime": package.create_time,
    })


@router.post("/create", summary="创建租户套餐")
async def create_tenant_package(
    name: str = Query(..., description="套餐名称"),
    status: int = Query(0, description="状态"),
    remark: str = Query(None, description="备注"),
    menu_ids: str = Query(None, description="关联的菜单编号列表"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:tenant-package:create")),
):
    """创建租户套餐"""
    package_id = await TenantPackageService.create(db, name, status, remark, menu_ids)
    return success(data=package_id)


@router.put("/update", summary="更新租户套餐")
async def update_tenant_package(
    id: int = Query(..., description="套餐编号"),
    name: str = Query(None, description="套餐名称"),
    status: int = Query(None, description="状态"),
    remark: str = Query(None, description="备注"),
    menu_ids: str = Query(None, description="关联的菜单编号列表"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:tenant-package:update")),
):
    """更新租户套餐"""
    result = await TenantPackageService.update(db, id, name, status, remark, menu_ids)
    return success(data=result)


@router.delete("/delete", summary="删除租户套餐")
async def delete_tenant_package(
    id: int = Query(..., description="套餐编号"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:tenant-package:delete")),
):
    """删除租户套餐"""
    result = await TenantPackageService.delete(db, id)
    return success(data=result)


@router.delete("/delete-list", summary="批量删除租户套餐")
async def delete_tenant_package_list(
    ids: List[int] = Query(..., description="套餐编号列表"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:tenant-package:delete")),
):
    """批量删除租户套餐"""
    count = await TenantPackageService.delete_list(db, ids)
    return success(data=count > 0)