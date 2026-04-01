"""
AI 聊天对话控制器
参考 ruoyi-vue-pro yudao-module-ai AiChatConversationController
"""
from typing import List
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import check_permission, get_current_user
from app.module.system.model.user import User
from app.module.ai.service.chat_conversation import ChatConversationService
from app.module.ai.schema.chat_conversation import (
    ChatConversationCreate,
    ChatConversationUpdate,
    ChatConversationResponse,
    ChatConversationPageQuery,
)
from app.common.response import success, page_success
from app.common.decorators import operate_log

router = APIRouter()


@router.get("/page", summary="获得对话分页")
async def get_conversation_page(
    query: ChatConversationPageQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:chat-conversation:query")),
):
    """分页查询对话列表（用于【对话管理】菜单）"""
    conversations, total = await ChatConversationService.get_page(db, query)

    if not conversations:
        return page_success(
            list_data=[],
            total=0,
            page_no=query.page_no,
            page_size=query.page_size,
        )

    # 获取消息数量
    conversation_ids = [c.id for c in conversations]
    message_count_map = await ChatConversationService.get_message_count_map(db, conversation_ids)

    # 构建响应
    conversation_responses = []
    for c in conversations:
        response_dict = {
            "id": c.id,
            "user_id": c.user_id,
            "title": c.title,
            "pinned": c.pinned,
            "pinned_time": c.pinned_time,
            "role_id": c.role_id,
            "model_id": c.model_id,
            "model": c.model,
            "system_message": c.system_message,
            "temperature": c.temperature,
            "max_tokens": c.max_tokens,
            "max_contexts": c.max_contexts,
            "create_time": c.create_time,
            "message_count": message_count_map.get(c.id, 0),
        }
        conversation_responses.append(ChatConversationResponse.model_validate(response_dict))

    return page_success(
        list_data=conversation_responses,
        total=total,
        page_no=query.page_no,
        page_size=query.page_size,
    )


@router.get("/my-list", summary="获得【我的】聊天对话列表")
async def get_my_conversation_list(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获得当前用户的聊天对话列表"""
    conversations = await ChatConversationService.get_list_by_user_id(db, current_user.id)
    conversation_responses = [ChatConversationResponse.model_validate(c) for c in conversations]
    return success(data=conversation_responses)


@router.get("/get-my", summary="获得【我的】聊天对话")
async def get_my_conversation(
    id: int = Query(..., description="对话编号"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获得当前用户的聊天对话详情"""
    conversation = await ChatConversationService.get_by_id(db, id)
    if not conversation or conversation.user_id != current_user.id:
        return success(data=None)
    return success(data=ChatConversationResponse.model_validate(conversation))


@router.get("/get", summary="获得对话详情")
async def get_conversation(
    id: int = Query(..., description="对话编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:chat-conversation:query")),
):
    """根据ID获取对话详情"""
    conversation = await ChatConversationService.get_by_id(db, id)
    if not conversation:
        return success(data=None)
    return success(data=ChatConversationResponse.model_validate(conversation))


@router.post("/create-my", summary="创建【我的】聊天对话")
async def create_my_conversation(
    conversation_create: ChatConversationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建当前用户的聊天对话"""
    # 设置当前用户ID
    conversation_create.user_id = current_user.id
    conversation = await ChatConversationService.create(db, conversation_create)
    return success(data=conversation.id)


@router.put("/update-my", summary="更新【我的】聊天对话")
@operate_log(type="AI 聊天对话", sub_type="更新对话")
async def update_my_conversation(
    request: Request,
    conversation_update: ChatConversationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新当前用户的聊天对话"""
    await ChatConversationService.delete_by_user(db, conversation_update.id, current_user.id)
    await ChatConversationService.update(db, conversation_update.id, conversation_update)
    return success(data=True)


@router.delete("/delete-my", summary="删除【我的】聊天对话")
@operate_log(type="AI 聊天对话", sub_type="删除对话")
async def delete_my_conversation(
    request: Request,
    id: int = Query(..., description="对话编号"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除当前用户的聊天对话"""
    await ChatConversationService.delete_by_user(db, id, current_user.id)
    return success(data=True)


@router.delete("/delete-by-unpinned", summary="删除未置顶的聊天对话")
@operate_log(type="AI 聊天对话", sub_type="删除未置顶对话")
async def delete_unpinned_conversation(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除当前用户未置顶的聊天对话"""
    count = await ChatConversationService.delete_unpinned_by_user(db, current_user.id)
    return success(data=count)


@router.delete("/delete-by-admin", summary="管理员删除对话")
@operate_log(type="AI 聊天对话管理", sub_type="管理员删除对话")
async def delete_conversation_by_admin(
    request: Request,
    id: int = Query(..., description="对话编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:chat-conversation:delete")),
):
    """管理员删除对话"""
    await ChatConversationService.delete(db, id)
    return success(data=True)