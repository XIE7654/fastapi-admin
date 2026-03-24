"""
站内信消息控制器
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.module.system.model.user import User
from app.module.system.service.notify_message import NotifyMessageService
from app.module.system.schema.log import NotifyMessagePageQuery
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


@router.get("/page", summary="获取站内信消息分页")
async def get_notify_message_page(
    page_no: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=10, ge=1, le=100, description="每页大小"),
    user_id: Optional[int] = Query(default=None, description="用户ID"),
    user_type: Optional[int] = Query(default=None, description="用户类型"),
    template_code: Optional[str] = Query(default=None, description="模板编码"),
    template_type: Optional[int] = Query(default=None, description="模板类型"),
    create_time: Optional[List[datetime]] = Query(default=None, description="创建时间范围"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取站内信消息分页列表

    Args:
        page_no: 页码
        page_size: 每页大小
        user_id: 用户ID
        user_type: 用户类型
        template_code: 模板编码
        template_type: 模板类型
        create_time: 创建时间范围
    """
    query = NotifyMessagePageQuery(
        page_no=page_no,
        page_size=page_size,
        user_id=user_id,
        user_type=user_type,
        template_code=template_code,
        template_type=template_type,
        create_time=create_time,
    )
    messages, total = await NotifyMessageService.get_page(db, query)
    return success(data={
        "list": [
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
        ],
        "total": total,
    })