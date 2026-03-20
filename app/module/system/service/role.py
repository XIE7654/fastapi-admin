"""
角色服务
"""
from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.system.model.role import Role, RoleMenu
from app.module.system.model.user import UserRole
from app.core.exceptions import BusinessException, ErrorCode


class RoleService:
    """角色服务"""

    @staticmethod
    async def get_by_id(db: AsyncSession, role_id: int) -> Optional[Role]:
        """根据ID获取角色"""
        result = await db.execute(
            select(Role).where(Role.id == role_id, Role.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_code(db: AsyncSession, code: str) -> Optional[Role]:
        """根据编码获取角色"""
        result = await db.execute(
            select(Role).where(Role.code == code, Role.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_roles(db: AsyncSession, user_id: int) -> List[Role]:
        """获取用户角色列表"""
        result = await db.execute(
            select(Role)
            .join(UserRole, Role.id == UserRole.role_id)
            .where(UserRole.user_id == user_id, Role.deleted == 0, Role.status == 0)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_all(db: AsyncSession) -> List[Role]:
        """获取所有角色"""
        result = await db.execute(
            select(Role)
            .where(Role.deleted == 0)
            .order_by(Role.sort.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_role_menu_ids(db: AsyncSession, role_id: int) -> List[int]:
        """获取角色的菜单ID列表"""
        result = await db.execute(
            select(RoleMenu.menu_id).where(RoleMenu.role_id == role_id)
        )
        return [row[0] for row in result.all()]