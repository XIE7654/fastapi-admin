"""
菜单控制器
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.module.system.model.user import User
from app.module.system.service.menu import MenuService
from app.common.response import success

router = APIRouter()


@router.post("/create", summary="创建菜单")
async def create_menu(
    name: str = Query(..., description="菜单名称"),
    permission: str = Query(None, description="权限标识"),
    type: int = Query(..., description="菜单类型: 1-目录, 2-菜单, 3-按钮"),
    sort: int = Query(0, description="显示顺序"),
    parent_id: int = Query(0, description="父菜单ID"),
    path: str = Query(None, description="路由地址"),
    icon: str = Query(None, description="菜单图标"),
    component: str = Query(None, description="组件路径"),
    component_name: str = Query(None, description="组件名称"),
    status: int = Query(0, description="状态"),
    visible: int = Query(0, description="是否可见"),
    keep_alive: int = Query(0, description="是否缓存"),
    always_show: int = Query(0, description="是否总是显示"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:menu:create")),
):
    """创建菜单"""
    menu_id = await MenuService.create(
        db, name, permission, type, sort, parent_id, path, icon,
        component, component_name, status, visible, keep_alive, always_show
    )
    return success(data=menu_id)


@router.put("/update", summary="修改菜单")
async def update_menu(
    id: int = Query(..., description="菜单ID"),
    name: str = Query(None, description="菜单名称"),
    permission: str = Query(None, description="权限标识"),
    type: int = Query(None, description="菜单类型"),
    sort: int = Query(None, description="显示顺序"),
    parent_id: int = Query(None, description="父菜单ID"),
    path: str = Query(None, description="路由地址"),
    icon: str = Query(None, description="菜单图标"),
    component: str = Query(None, description="组件路径"),
    component_name: str = Query(None, description="组件名称"),
    status: int = Query(None, description="状态"),
    visible: int = Query(None, description="是否可见"),
    keep_alive: int = Query(None, description="是否缓存"),
    always_show: int = Query(None, description="是否总是显示"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:menu:update")),
):
    """更新菜单"""
    await MenuService.update(
        db, id, name, permission, type, sort, parent_id, path, icon,
        component, component_name, status, visible, keep_alive, always_show
    )
    return success(data=True)


@router.delete("/delete", summary="删除菜单")
async def delete_menu(
    id: int = Query(..., description="菜单ID"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:menu:delete")),
):
    """删除菜单"""
    await MenuService.delete(db, id)
    return success(data=True)


@router.get("/list", summary="获取菜单列表")
async def get_menu_list(
    name: str = Query(None, description="菜单名称"),
    status: int = Query(None, description="状态"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:menu:list")),
):
    """获取菜单列表"""
    menus = await MenuService.get_all(db, name, status)
    return success(data=menus)


@router.get("/get", summary="获得菜单信息")
async def get_menu(
    id: int = Query(..., description="菜单ID"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:menu:query")),
):
    """根据ID获取菜单详情"""
    menu = await MenuService.get_by_id(db, id)
    if not menu:
        return success(data=None)
    return success(data={
        "id": menu.id,
        "name": menu.name,
        "permission": menu.permission,
        "type": menu.type,
        "sort": menu.sort,
        "parentId": menu.parent_id,
        "path": menu.path,
        "icon": menu.icon,
        "component": menu.component,
        "componentName": menu.component_name,
        "status": menu.status,
        "visible": menu.visible,
        "keepAlive": menu.keep_alive,
        "alwaysShow": menu.always_show,
        "createTime": menu.create_time,
    })