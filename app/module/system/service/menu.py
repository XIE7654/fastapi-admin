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
    async def get_all(db: AsyncSession, name: str = None, status: int = None) -> List[Menu]:
        """获取所有菜单"""
        query = select(Menu)

        # 添加过滤条件
        if name:
            query = query.where(Menu.name.like(f"%{name}%"))
        if status is not None:
            query = query.where(Menu.status == status)

        query = query.order_by(Menu.sort.asc())
        result = await db.execute(query)
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
        """获取用户的菜单树（只包含目录和菜单，不包含按钮）"""
        menu_ids = await MenuService.get_user_menu_ids(db, user_id)
        if not menu_ids:
            return []

        # 查询菜单，过滤掉按钮类型(type=3)，只保留目录(type=1)和菜单(type=2)
        result = await db.execute(
            select(Menu)
            .where(Menu.id.in_(menu_ids), Menu.status == 0, Menu.type != 3)
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
    async def create(
        db: AsyncSession,
        name: str,
        permission: str,
        type: int,
        sort: int,
        parent_id: int,
        path: str,
        icon: str,
        component: str,
        component_name: str,
        status: int,
        visible: int,
        keep_alive: int,
        always_show: int,
    ) -> int:
        """创建菜单"""
        menu = Menu(
            name=name,
            permission=permission or "",
            type=type,
            sort=sort,
            parent_id=parent_id,
            path=path or "",
            icon=icon or "",
            component=component or "",
            component_name=component_name or "",
            status=status,
            visible=visible,
            keep_alive=keep_alive,
            always_show=always_show,
        )
        db.add(menu)
        await db.flush()
        await db.refresh(menu)
        return menu.id

    @staticmethod
    async def update(
        db: AsyncSession,
        menu_id: int,
        name: str,
        permission: str,
        type: int,
        sort: int,
        parent_id: int,
        path: str,
        icon: str,
        component: str,
        component_name: str,
        status: int,
        visible: int,
        keep_alive: int,
        always_show: int,
    ) -> None:
        """更新菜单"""
        menu = await MenuService.get_by_id(db, menu_id)
        if menu:
            menu.name = name
            menu.permission = permission or ""
            menu.type = type
            menu.sort = sort
            menu.parent_id = parent_id
            menu.path = path or ""
            menu.icon = icon or ""
            menu.component = component or ""
            menu.component_name = component_name or ""
            menu.status = status
            menu.visible = visible
            menu.keep_alive = keep_alive
            menu.always_show = always_show

    @staticmethod
    async def delete(db: AsyncSession, menu_id: int) -> None:
        """删除菜单"""
        menu = await MenuService.get_by_id(db, menu_id)
        if menu:
            await db.delete(menu)

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