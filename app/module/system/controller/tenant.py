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