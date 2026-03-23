"""
租户控制器
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.module.system.model.user import User
from app.module.system.service.tenant import TenantService
from app.common.response import success, page_success

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
    website: str = Query(..., description="域名", pattern=r"^[a-zA-Z0-9.-]+$"),
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


@router.get("/get-id-by-name", summary="使用租户名获得租户编号")
async def get_tenant_id_by_name(
    name: str = Query(..., description="租户名"),
    db: AsyncSession = Depends(get_db),
):
    """使用租户名，获得租户编号，用于登录界面根据用户的租户名获得租户编号"""
    tenant = await TenantService.get_tenant_by_name(db, name)
    return success(data=tenant.id if tenant else None)


@router.get("/page", summary="获得租户分页")
async def get_tenant_page(
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    name: str = Query(None, description="租户名"),
    contact_name: str = Query(None, description="联系人"),
    contact_mobile: str = Query(None, description="联系手机"),
    status: int = Query(None, description="状态"),
    package_id: int = Query(None, description="租户套餐编号"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:tenant:query")),
):
    """分页查询租户列表"""
    tenants, total = await TenantService.get_page(
        db, page_no, page_size, name, contact_name, contact_mobile, status, package_id
    )
    return page_success(
        list_data=[
            {
                "id": t.id,
                "name": t.name,
                "contactName": t.contact_name,
                "contactMobile": t.contact_mobile,
                "status": t.status,
                "websites": t.websites.split(",") if t.websites else [],
                "packageId": t.package_id,
                "expireTime": t.expire_time.isoformat() if t.expire_time else None,
                "accountCount": t.account_count,
                "createTime": t.create_time,
            }
            for t in tenants
        ],
        total=total,
        page_no=page_no,
        page_size=page_size,
    )


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
        "websites": tenant.websites.split(",") if tenant.websites else [],
        "packageId": tenant.package_id,
        "expireTime": tenant.expire_time.isoformat() if tenant.expire_time else None,
        "accountCount": tenant.account_count,
        "remark": tenant.remark,
        "createTime": tenant.create_time,
    })