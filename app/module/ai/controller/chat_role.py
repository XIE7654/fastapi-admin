"""
AI 聊天角色控制器
参考 ruoyi-vue-pro yudao-module-ai 模块的 AiChatRoleController
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import check_permission
from app.module.system.model.user import User
from app.module.ai.service.chat_role import ChatRoleService
from app.module.ai.schema.chat_role import (
    ChatRoleCreate,
    ChatRoleUpdate,
    ChatRoleResponse,
    ChatRolePageQuery,
)
from app.common.response import success, page_success
from app.common.decorators import operate_log

router = APIRouter()


@router.post("/create", summary="创建聊天角色")
@operate_log(type="AI 聊天角色管理", sub_type="创建聊天角色")
async def create_chat_role(
    request: Request,
    role_create: ChatRoleCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:chat-role:create")),
):
    """创建 AI 聊天角色"""
    role = await ChatRoleService.create(db, role_create)
    return success(data=role.id)


@router.put("/update", summary="更新聊天角色")
@operate_log(type="AI 聊天角色管理", sub_type="更新聊天角色")
async def update_chat_role(
    request: Request,
    role_update: ChatRoleUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:chat-role:update")),
):
    """更新 AI 聊天角色"""
    await ChatRoleService.update(db, role_update.id, role_update)
    return success(data=True)


@router.delete("/delete", summary="删除聊天角色")
@operate_log(type="AI 聊天角色管理", sub_type="删除聊天角色")
async def delete_chat_role(
    request: Request,
    id: int = Query(..., description="角色编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:chat-role:delete")),
):
    """删除 AI 聊天角色"""
    await ChatRoleService.delete(db, id)
    return success(data=True)


@router.get("/get", summary="获得聊天角色")
async def get_chat_role(
    id: int = Query(..., description="角色编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:chat-role:query")),
):
    """根据 ID 获取聊天角色详情"""
    role = await ChatRoleService.get_by_id(db, id)
    if not role:
        return success(data=None)
    return success(data=ChatRoleResponse.model_validate(role))


@router.get("/page", summary="获得聊天角色分页")
async def get_chat_role_page(
    query: ChatRolePageQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:chat-role:query")),
):
    """分页查询聊天角色列表"""
    roles, total = await ChatRoleService.get_list(db, query)
    role_responses = [ChatRoleResponse.model_validate(r) for r in roles]
    return page_success(
        list_data=role_responses,
        total=total,
        page_no=query.page_no,
        page_size=query.page_size,
    )