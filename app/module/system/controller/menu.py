"""
菜单控制器
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.module.system.model.user import User
from app.module.system.service.menu import MenuService
from app.module.system.schema.menu import MenuSave
from app.common.response import success

router = APIRouter()


@router.post("/create", summary="创建菜单")
async def create_menu(
    req: MenuSave = Body(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:menu:create")),
):
    """创建菜单"""
    menu_id = await MenuService.create(
        db, req.name, req.permission, req.type, req.sort, req.parent_id,
        req.path, req.icon, req.component, req.component_name,
        req.status, 1 if req.visible else 0, 1 if req.keep_alive else 0, 1 if req.always_show else 0
    )
    return success(data=menu_id)


@router.put("/update", summary="修改菜单")
async def update_menu(
    req: MenuSave = Body(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:menu:update")),
):
    """更新菜单"""
    if not req.id:
        return success(data=False, message="菜单ID不能为空")
    await MenuService.update(
        db, req.id, req.name, req.permission, req.type, req.sort, req.parent_id,
        req.path, req.icon, req.component, req.component_name,
        req.status, 1 if req.visible else 0, 1 if req.keep_alive else 0, 1 if req.always_show else 0
    )
    return success(data=True)


@router.delete("/delete", summary="删除菜单")
async def delete_menu(
    id: int = Query(..., description="菜单ID"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:menu:delete")),
):
    """删除菜单"""
    await MenuService.delete(db, id)
    return success(data=True)


@router.get("/list", summary="获取菜单列表")
async def get_menu_list(
    name: str = Query(None, description="菜单名称"),
    status: int = Query(None, description="状态"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:menu:query")),
):
    """获取菜单列表"""
    menus = await MenuService.get_all(db, name, status)
    # 序列化菜单列表
    menu_list = []
    for menu in menus:
        menu_list.append({
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
            "createTime": menu.create_time.isoformat() if menu.create_time else None,
        })
    return success(data=menu_list)


@router.get("/simple-list", summary="获取菜单精简信息列表")
async def get_simple_menu_list(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取菜单精简信息列表（只包含被开启的菜单，用于角色分配菜单功能的选项）"""
    menus = await MenuService.get_all(db, status=0)
    # 序列化菜单列表
    menu_list = []
    for menu in menus:
        menu_list.append({
            "id": menu.id,
            "name": menu.name,
            "permission": menu.permission,
            "parentId": menu.parent_id,
            "type": menu.type,
        })
    return success(data=menu_list)


@router.get("/get", summary="获得菜单信息")
async def get_menu(
    id: int = Query(..., description="菜单ID"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:menu:query")),
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