"""
权限服务
"""
from typing import Set, List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.system.model.user import UserRole
from app.module.system.model.role import RoleMenu


class PermissionService:
    """权限服务类"""

    @staticmethod
    async def get_user_role_id_list(db: AsyncSession, user_id: int) -> Set[int]:
        """
        获取用户拥有的角色编号列表

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            角色ID集合
        """
        result = await db.execute(
            select(UserRole.role_id).where(UserRole.user_id == user_id)
        )
        return {row[0] for row in result.all()}

    @staticmethod
    async def get_role_menu_id_list(db: AsyncSession, role_id: int) -> Set[int]:
        """
        获取角色拥有的菜单编号列表

        Args:
            db: 数据库会话
            role_id: 角色ID

        Returns:
            菜单ID集合
        """
        result = await db.execute(
            select(RoleMenu.menu_id).where(RoleMenu.role_id == role_id)
        )
        return {row[0] for row in result.all()}

    @staticmethod
    async def assign_user_roles(db: AsyncSession, user_id: int, role_ids: Set[int]) -> bool:
        """
        分配用户角色

        Args:
            db: 数据库会话
            user_id: 用户ID
            role_ids: 角色ID集合

        Returns:
            是否成功
        """
        # 获取当前用户的角色
        current_role_ids = await PermissionService.get_user_role_id_list(db, user_id)

        # 计算新增和删除的角色
        create_role_ids = role_ids - current_role_ids
        delete_role_ids = current_role_ids - role_ids

        # 删除不再需要的角色关联
        if delete_role_ids:
            await db.execute(
                delete(UserRole).where(
                    UserRole.user_id == user_id,
                    UserRole.role_id.in_(delete_role_ids)
                )
            )

        # 添加新的角色关联
        if create_role_ids:
            for role_id in create_role_ids:
                user_role = UserRole(user_id=user_id, role_id=role_id)
                db.add(user_role)

        await db.flush()
        return True

    @staticmethod
    async def assign_role_menus(db: AsyncSession, role_id: int, menu_ids: Set[int]) -> bool:
        """
        分配角色菜单

        Args:
            db: 数据库会话
            role_id: 角色ID
            menu_ids: 菜单ID集合

        Returns:
            是否成功
        """
        # 获取当前角色的菜单
        current_menu_ids = await PermissionService.get_role_menu_id_list(db, role_id)

        # 计算新增和删除的菜单
        create_menu_ids = menu_ids - current_menu_ids
        delete_menu_ids = current_menu_ids - menu_ids

        # 删除不再需要的菜单关联
        if delete_menu_ids:
            await db.execute(
                delete(RoleMenu).where(
                    RoleMenu.role_id == role_id,
                    RoleMenu.menu_id.in_(delete_menu_ids)
                )
            )

        # 添加新的菜单关联
        if create_menu_ids:
            for menu_id in create_menu_ids:
                role_menu = RoleMenu(role_id=role_id, menu_id=menu_id)
                db.add(role_menu)

        await db.flush()
        return True