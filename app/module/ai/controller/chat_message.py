"""
AI 聊天消息控制器
参考 ruoyi-vue-pro yudao-module-ai AiChatMessageController
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import check_permission, get_current_user
from app.module.system.model.user import User
from app.module.ai.service.chat_message import ChatMessageService
from app.module.ai.schema.chat_message import (
    ChatMessageResponse,
    ChatMessagePageQuery,
    ChatMessageSendReqVO,
    ChatMessageSendRespVO,
)
from app.common.response import success, page_success
from app.common.decorators import operate_log

router = APIRouter()


@router.post("/send", summary="发送消息（段式）")
async def send_message(
    send_req: ChatMessageSendReqVO,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """发送消息（一次性返回，响应较慢）"""
    result = await ChatMessageService.send_message(db, send_req, current_user.id)
    return success(data=result)


@router.post("/send-stream", summary="发送消息（流式）")
async def send_message_stream(
    send_req: ChatMessageSendReqVO,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """发送消息（流式返回，响应较快）"""
    return StreamingResponse(
        ChatMessageService.send_message_stream(db, send_req, current_user.id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/page", summary="获得消息分页")
async def get_message_page(
    query: ChatMessagePageQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:chat-conversation:query")),
):
    """分页查询消息列表（用于【对话管理】菜单）"""
    messages, total = await ChatMessageService.get_page(db, query)
    message_responses = [ChatMessageResponse.model_validate(m) for m in messages]
    return page_success(
        list_data=message_responses,
        total=total,
        page_no=query.page_no,
        page_size=query.page_size,
    )


@router.get("/list-by-conversation-id", summary="获得指定对话的消息列表")
async def get_message_list_by_conversation_id(
    conversationId: int = Query(..., alias="conversationId", description="对话编号"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """根据对话ID获取消息列表"""
    messages = await ChatMessageService.get_list_by_conversation_id(db, conversationId)
    message_responses = [ChatMessageResponse.model_validate(m) for m in messages]
    return success(data=message_responses)


@router.delete("/delete", summary="删除消息")
@operate_log(type="AI 聊天消息", sub_type="删除消息")
async def delete_message(
    request: Request,
    id: int = Query(..., description="消息编号"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除消息"""
    await ChatMessageService.delete(db, id)
    return success(data=True)


@router.delete("/delete-by-conversation-id", summary="删除指定对话的消息")
@operate_log(type="AI 聊天消息", sub_type="删除对话消息")
async def delete_message_by_conversation_id(
    request: Request,
    conversationId: int = Query(..., alias="conversationId", description="对话编号"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除指定对话的所有消息"""
    await ChatMessageService.delete_by_conversation_id(db, conversationId)
    return success(data=True)


@router.delete("/delete-by-admin", summary="管理员删除消息")
@operate_log(type="AI 聊天消息管理", sub_type="管理员删除消息")
async def delete_message_by_admin(
    request: Request,
    id: int = Query(..., description="消息编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:chat-message:delete")),
):
    """管理员删除消息"""
    await ChatMessageService.delete(db, id)
    return success(data=True)