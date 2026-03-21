"""
站内信消息控制器
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.module.system.model.user import User
from app.module.system.service.notify_message import NotifyMessageService
from app.common.response import success

router = APIRouter()


@router.get("/get-unread-count", summary="获得当前用户的未读站内信数量")
async def get_unread_notify_message_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取当前用户的未读站内信数量

    无需权限认证，所有登录用户都可访问
    """
    count = await NotifyMessageService.get_unread_count(
        db,
        user_id=current_user.id,
        user_type=NotifyMessageService.USER_TYPE_ADMIN
    )
    # Java 版本返回 Long 类型
    return success(data=count)


@router.get("/get-unread-list", summary="获取当前用户的最新未读站内信列表")
async def get_unread_notify_message_list(
    size: int = Query(default=10, ge=1, le=100, description="返回数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取当前用户的最新未读站内信列表

    Args:
        size: 返回数量，默认10条
    """
    messages = await NotifyMessageService.get_unread_list(
        db,
        user_id=current_user.id,
        user_type=NotifyMessageService.USER_TYPE_ADMIN,
        size=size
    )
    return success(data=[
        {
            "id": msg.id,
            "userId": msg.user_id,
            "userType": msg.user_type,
            "templateId": msg.template_id,
            "templateCode": msg.template_code,
            "templateNickname": msg.template_nickname,
            "templateContent": msg.template_content,
            "templateType": msg.template_type,
            "templateParams": msg.template_params,
            "readStatus": msg.read_status == 1,
            "readTime": msg.read_time,
            "createTime": msg.create_time,
        }
        for msg in messages
    ])


@router.put("/update-read", summary="标记站内信为已读")
async def update_notify_message_read(
    ids: List[int] = Query(..., description="站内信编号列表"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    标记站内信为已读

    Args:
        ids: 站内信编号列表
    """
    count = await NotifyMessageService.mark_as_read(
        db,
        message_ids=ids,
        user_id=current_user.id,
        user_type=NotifyMessageService.USER_TYPE_ADMIN
    )
    return success(data=count > 0)


@router.put("/update-all-read", summary="标记所有站内信为已读")
async def update_all_notify_message_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """标记所有站内信为已读"""
    count = await NotifyMessageService.mark_all_as_read(
        db,
        user_id=current_user.id,
        user_type=NotifyMessageService.USER_TYPE_ADMIN
    )
    return success(data=True)