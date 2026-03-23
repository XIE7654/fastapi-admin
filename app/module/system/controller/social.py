"""
社交客户端和社交用户控制器
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.module.system.service.social import SocialClientService, SocialUserService
from app.common.response import success, page_success

# 社交客户端路由
router_client = APIRouter()

# 社交用户路由
router_user = APIRouter()


@router_client.get("/page", summary="获得社交客户端分页")
async def get_social_client_page(
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    name: str = Query(None, description="应用名"),
    social_type: int = Query(None, description="社交类型"),
    user_type: int = Query(None, description="用户类型"),
    status: int = Query(None, description="状态"),
    db: AsyncSession = Depends(get_db),
):
    """分页查询社交客户端"""
    clients, total = await SocialClientService.get_page(
        db, page_no, page_size, name, social_type, user_type, status
    )
    return page_success(
        list_data=[
            {
                "id": c.id,
                "name": c.name,
                "socialType": c.social_type,
                "userType": c.user_type,
                "clientId": c.client_id,
                "clientSecret": c.client_secret,
                "agentId": c.agent_id,
                "status": c.status,
                "remark": c.remark,
                "createTime": c.create_time,
            }
            for c in clients
        ],
        total=total,
        page_no=page_no,
        page_size=page_size,
    )


@router_client.get("/get", summary="获得社交客户端")
async def get_social_client(
    id: int = Query(..., description="客户端编号"),
    db: AsyncSession = Depends(get_db),
):
    """根据ID获取社交客户端详情"""
    client = await SocialClientService.get_by_id(db, id)
    if not client:
        return success(data=None)
    return success(data={
        "id": client.id,
        "name": client.name,
        "socialType": client.social_type,
        "userType": client.user_type,
        "clientId": client.client_id,
        "clientSecret": client.client_secret,
        "agentId": client.agent_id,
        "status": client.status,
        "remark": client.remark,
        "createTime": client.create_time,
    })


@router_user.get("/page", summary="获得社交用户分页")
async def get_social_user_page(
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    type: int = Query(None, description="社交类型"),
    openid: str = Query(None, description="社交openid"),
    nickname: str = Query(None, description="用户昵称"),
    db: AsyncSession = Depends(get_db),
):
    """分页查询社交用户"""
    users, total = await SocialUserService.get_page(
        db, page_no, page_size, type, openid, nickname
    )
    return page_success(
        list_data=[
            {
                "id": u.id,
                "type": u.type,
                "openid": u.openid,
                "token": u.token,
                "rawTokenInfo": u.raw_token_info,
                "nickname": u.nickname,
                "avatar": u.avatar,
                "rawUserInfo": u.raw_user_info,
                "createTime": u.create_time,
            }
            for u in users
        ],
        total=total,
        page_no=page_no,
        page_size=page_size,
    )


@router_user.get("/get", summary="获得社交用户")
async def get_social_user(
    id: int = Query(..., description="用户编号"),
    db: AsyncSession = Depends(get_db),
):
    """根据ID获取社交用户详情"""
    user = await SocialUserService.get_by_id(db, id)
    if not user:
        return success(data=None)
    return success(data={
        "id": user.id,
        "type": user.type,
        "openid": user.openid,
        "token": user.token,
        "rawTokenInfo": user.raw_token_info,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "rawUserInfo": user.raw_user_info,
        "createTime": user.create_time,
    })