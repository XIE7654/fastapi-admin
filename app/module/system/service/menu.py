"""
菜单服务
"""
from typing import Optional, List, Set
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.system.model.menu import Menu
from app.module.system.model.role import RoleMenu
from app.module.system.model.user import UserRole
from app.module.system.schema.auth import MenuVO


class MenuService:
    """菜单服务"""

    @staticmethod
    async def get_by_id(db: AsyncSession, menu_id: int) -> Optional[Menu]:
        """根据ID获取菜单"""
        result = await db.execute(
            select(Menu).where(Menu.id == menu_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession) -> List[Menu]:
        """获取所有菜单"""
        result = await db.execute(
            select(Menu).order_by(Menu.sort.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_user_menu_ids(db: AsyncSession, user_id: int) -> List[int]:
        """获取用户的菜单ID列表"""
        # 超级管理员拥有所有菜单
        if user_id == 1:
            menus = await MenuService.get_all(db)
            return [m.id for m in menus]

        # 查询用户角色关联的菜单
        result = await db.execute(
            select(RoleMenu.menu_id)
            .join(UserRole, RoleMenu.role_id == UserRole.role_id)
            .where(UserRole.user_id == user_id)
            .distinct()
        )
        return [row[0] for row in result.all()]

    @staticmethod
    async def get_user_menus(db: AsyncSession, user_id: int) -> List[dict]:
        """获取用户的菜单树"""
        menu_ids = await MenuService.get_user_menu_ids(db, user_id)
        if not menu_ids:
            return []

        # 查询菜单
        result = await db.execute(
            select(Menu)
            .where(Menu.id.in_(menu_ids), Menu.status == 0)
            .order_by(Menu.sort.asc())
        )
        menus = list(result.scalars().all())

        # 构建菜单树
        return MenuService._build_menu_tree(menus, 0)

    @staticmethod
    async def get_user_permissions(db: AsyncSession, user_id: int) -> Set[str]:
        """获取用户权限标识列表"""
        # 超级管理员拥有所有权限
        if user_id == 1:
            result = await db.execute(
                select(Menu.permission).where(Menu.permission.isnot(None))
            )
            return {row[0] for row in result.all() if row[0]}

        # 查询用户角色关联的菜单权限
        result = await db.execute(
            select(Menu.permission)
            .join(RoleMenu, Menu.id == RoleMenu.menu_id)
            .join(UserRole, RoleMenu.role_id == UserRole.role_id)
            .where(UserRole.user_id == user_id, Menu.permission.isnot(None))
        )
        return {row[0] for row in result.all() if row[0]}

    @staticmethod
    def _build_menu_tree(menus: List[Menu], parent_id: int) -> List[dict]:
        """构建菜单树"""
        result = []
        for menu in menus:
            if menu.parent_id == parent_id:
                menu_dict = {
                    "id": menu.id,
                    "name": menu.name,
                    "parentId": menu.parent_id,
                    "path": menu.path,
                    "icon": menu.icon,
                    "component": menu.component,
                    "componentName": menu.component_name,
                    "sort": menu.sort,
                    "visible": menu.visible,
                    "keepAlive": menu.keep_alive,
                    "type": menu.type,
                    "permission": menu.permission,
                }
                # 递归获取子菜单
                children = MenuService._build_menu_tree(menus, menu.id)
                if children:
                    menu_dict["children"] = children
                result.append(menu_dict)
        return result