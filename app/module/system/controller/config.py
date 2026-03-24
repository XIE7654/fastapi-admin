"""
参数配置控制器
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.module.system.model.user import User
from app.module.system.service.config import ConfigService
from app.module.system.schema.config import (
    ConfigCreate,
    ConfigUpdate,
    ConfigResponse,
    ConfigPageQuery,
)
from app.common.response import success, page_success

router = APIRouter()


@router.get("/page", summary="获取参数配置分页列表")
async def get_config_page(
    query: ConfigPageQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:config:query")),
):
    """分页查询参数配置"""
    configs, total = await ConfigService.get_list(db, query)
    return page_success(
        list_data=[ConfigResponse.model_validate(c) for c in configs],
        total=total,
        page_no=query.page_no,
        page_size=query.page_size,
    )


@router.get("/get", summary="获取参数配置详情")
async def get_config(
    id: int = Query(None, description="配置ID"),
    key: str = Query(None, description="配置键名"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:config:query")),
):
    """根据ID或键名获取配置详情"""
    if id:
        config = await ConfigService.get_by_id(db, id)
    elif key:
        config = await ConfigService.get_by_key(db, key)
    else:
        return success(msg="请提供id或key参数")

    if not config:
        return success(msg="配置不存在")
    return success(data=ConfigResponse.model_validate(config))


@router.get("/value", summary="获取配置值")
async def get_config_value(
    key: str = Query(..., description="配置键名"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """根据键名获取配置值"""
    value = await ConfigService.get_value(db, key)
    return success(data=value)


@router.post("/create", summary="创建参数配置")
async def create_config(
    config_create: ConfigCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:config:create")),
):
    """创建参数配置"""
    config = await ConfigService.create(db, config_create)
    return success(data=ConfigResponse.model_validate(config), msg="创建成功")


@router.put("/update", summary="更新参数配置")
async def update_config(
    config_update: ConfigUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:config:update")),
):
    """更新参数配置"""
    config = await ConfigService.update(db, config_update.id, config_update)
    return success(data=ConfigResponse.model_validate(config), msg="更新成功")


@router.delete("/delete", summary="删除参数配置")
async def delete_config(
    id: int = Query(..., description="配置ID"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:config:delete")),
):
    """删除参数配置"""
    await ConfigService.delete(db, id)
    return success(msg="删除成功")