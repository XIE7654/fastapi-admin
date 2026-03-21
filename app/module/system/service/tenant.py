"""
租户服务
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.system.model.tenant import Tenant
from app.core.redis import get_cache, set_cache, RedisKeyPrefix
from app.core.exceptions import BusinessException, ErrorCode


class TenantService:
    """租户服务"""

    @staticmethod
    async def get_by_id(db: AsyncSession, tenant_id: int) -> Optional[Tenant]:
        """根据ID获取租户"""
        # 优先从缓存获取
        cache_key = f"{RedisKeyPrefix.TENANT}{tenant_id}"
        cached = await get_cache(cache_key)
        if cached:
            # TODO: 反序列化
            pass

        result = await db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        tenant = result.scalar_one_or_none()

        if tenant:
            # 缓存租户信息
            await set_cache(cache_key, tenant.name, expire=3600)

        return tenant

    @staticmethod
    async def get_valid_tenant(db: AsyncSession, tenant_id: int) -> Tenant:
        """获取有效的租户（检查状态和过期时间）"""
        tenant = await TenantService.get_by_id(db, tenant_id)

        if not tenant:
            raise BusinessException(code=ErrorCode.TENANT_NOT_EXISTS, message="租户不存在")

        if tenant.status != 0:
            raise BusinessException(code=ErrorCode.TENANT_DISABLED, message="租户已被禁用")

        if tenant.is_expired:
            raise BusinessException(code=ErrorCode.TENANT_EXPIRED, message="租户已过期")

        return tenant

    @staticmethod
    async def get_all(db: AsyncSession) -> List[Tenant]:
        """获取所有租户"""
        result = await db.execute(
            select(Tenant).order_by(Tenant.id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_tenant_ids_by_package_id(db: AsyncSession, package_id: int) -> List[int]:
        """根据套餐ID获取租户ID列表"""
        result = await db.execute(
            select(Tenant.id).where(Tenant.package_id == package_id)
        )
        return [row[0] for row in result.all()]

    @staticmethod
    async def get_tenant_list_by_status(db: AsyncSession, status: int) -> List[Tenant]:
        """根据状态获取租户列表"""
        result = await db.execute(
            select(Tenant).where(Tenant.status == status).order_by(Tenant.id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_tenant_by_website(db: AsyncSession, website: str) -> Optional[Tenant]:
        """根据域名获取租户"""
        # 使用 FIND_IN_SET 或 LIKE 查询 websites 字段
        # websites 字段存储的是逗号分隔的域名列表
        from sqlalchemy import text
        result = await db.execute(
            select(Tenant).where(
                text("FIND_IN_SET(:website, websites) > 0")
            ).params(website=website)
        )
        return result.scalar_one_or_none()