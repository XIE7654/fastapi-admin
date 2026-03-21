"""
租户控制器
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.module.system.model.user import User
from app.module.system.service.tenant import TenantService
from app.common.response import success

router = APIRouter()


@router.get("/simple-list", summary="获取租户精简信息列表")
async def get_tenant_simple_list(
    db: AsyncSession = Depends(get_db),
):
    """获取租户精简信息列表，只包含被开启的租户，用于首页功能的选择租户选项"""
    # 只获取状态为0（启用）的租户
    tenants = await TenantService.get_tenant_list_by_status(db, status=0)
    return success(data=[
        {
            "id": t.id,
            "name": t.name,
        }
        for t in tenants
    ])


@router.get("/get-by-website", summary="根据域名获取租户信息")
async def get_tenant_by_website(
    website: str = Query(..., description="域名", regex=r"^[a-zA-Z0-9.-]+$"),
    db: AsyncSession = Depends(get_db),
):
    """根据域名获取租户信息，用于登录界面根据用户的域名获得租户信息"""
    tenant = await TenantService.get_tenant_by_website(db, website)
    # 如果租户不存在或被禁用，返回null
    if not tenant or tenant.status != 0:
        return success(data=None)
    return success(data={
        "id": tenant.id,
        "name": tenant.name,
    })


@router.get("/list", summary="获取租户列表")
async def get_tenant_list(
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:tenant:list")),
):
    """获取所有租户列表"""
    tenants = await TenantService.get_all(db)
    return success(data=[
        {
            "id": t.id,
            "name": t.name,
            "contactName": t.contact_name,
            "contactMobile": t.contact_mobile,
            "status": t.status,
            "packageId": t.package_id,
            "expireTime": t.expire_time.isoformat() if t.expire_time else None,
        }
        for t in tenants
    ])


@router.get("/get", summary="获取租户详情")
async def get_tenant(
    id: int = Query(..., description="租户ID"),
    db: AsyncSession = Depends(get_db),
):
    """获取租户详情"""
    tenant = await TenantService.get_by_id(db, id)
    if not tenant:
        return success(msg="租户不存在")
    return success(data={
        "id": tenant.id,
        "name": tenant.name,
        "contactName": tenant.contact_name,
        "contactMobile": tenant.contact_mobile,
        "status": tenant.status,
        "packageId": tenant.package_id,
        "expireTime": tenant.expire_time.isoformat() if tenant.expire_time else None,
        "accountCount": tenant.account_count,
        "website": tenant.website,
        "remark": tenant.remark,
    })