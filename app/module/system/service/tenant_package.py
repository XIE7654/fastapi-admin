"""
租户套餐服务
"""
import json
from typing import Optional, List, Union
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.system.model.tenant import TenantPackage


class TenantPackageService:
    """租户套餐服务"""

    @staticmethod
    async def get_by_id(db: AsyncSession, package_id: int) -> Optional[TenantPackage]:
        """根据ID获取租户套餐"""
        result = await db.execute(
            select(TenantPackage).where(TenantPackage.id == package_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession) -> List[TenantPackage]:
        """获取所有租户套餐"""
        result = await db.execute(
            select(TenantPackage).order_by(TenantPackage.id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_list_by_status(db: AsyncSession, status: int) -> List[TenantPackage]:
        """根据状态获取租户套餐列表"""
        result = await db.execute(
            select(TenantPackage)
            .where(TenantPackage.status == status)
            .order_by(TenantPackage.id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_page(
        db: AsyncSession,
        page_no: int = 1,
        page_size: int = 10,
        name: str = None,
        status: int = None,
    ) -> tuple[List[TenantPackage], int]:
        """分页获取租户套餐"""
        # 构建查询条件
        conditions = []
        if name:
            conditions.append(TenantPackage.name.like(f"%{name}%"))
        if status is not None:
            conditions.append(TenantPackage.status == status)

        # 查询总数
        count_query = select(func.count(TenantPackage.id))
        if conditions:
            count_query = count_query.where(*conditions)
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 查询列表
        query = select(TenantPackage)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(TenantPackage.id.desc())
        query = query.offset((page_no - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    @staticmethod
    async def create(
        db: AsyncSession,
        name: str,
        status: int = 0,
        remark: str = None,
        menu_ids: Union[List[int], str] = None,
    ) -> int:
        """创建租户套餐"""
        # 将列表转为 JSON 字符串存储
        menu_ids_str = None
        if menu_ids is not None:
            if isinstance(menu_ids, list):
                menu_ids_str = json.dumps(menu_ids)
            else:
                menu_ids_str = menu_ids

        package = TenantPackage(
            name=name,
            status=status,
            remark=remark,
            menu_ids=menu_ids_str,
        )
        db.add(package)
        await db.commit()
        await db.refresh(package)
        return package.id

    @staticmethod
    async def update(
        db: AsyncSession,
        package_id: int,
        name: str = None,
        status: int = None,
        remark: str = None,
        menu_ids: Union[List[int], str] = None,
    ) -> bool:
        """更新租户套餐"""
        package = await TenantPackageService.get_by_id(db, package_id)
        if not package:
            return False

        if name is not None:
            package.name = name
        if status is not None:
            package.status = status
        if remark is not None:
            package.remark = remark
        if menu_ids is not None:
            # 将列表转为 JSON 字符串存储
            if isinstance(menu_ids, list):
                package.menu_ids = json.dumps(menu_ids)
            else:
                package.menu_ids = menu_ids

        await db.commit()
        return True

    @staticmethod
    async def delete(db: AsyncSession, package_id: int) -> bool:
        """删除租户套餐"""
        package = await TenantPackageService.get_by_id(db, package_id)
        if not package:
            return False

        await db.delete(package)
        await db.commit()
        return True

    @staticmethod
    async def delete_list(db: AsyncSession, package_ids: List[int]) -> int:
        """批量删除租户套餐"""
        count = 0
        for package_id in package_ids:
            if await TenantPackageService.delete(db, package_id):
                count += 1
        return count