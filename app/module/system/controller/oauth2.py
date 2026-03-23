"""
OAuth2 客户端控制器
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import check_permission
from app.module.system.model.user import User
from app.module.system.service.oauth2_client import OAuth2ClientService, OAuth2AccessTokenService
from app.common.response import success, page_success

# OAuth2 客户端路由
router_client = APIRouter()

# OAuth2 令牌路由
router_token = APIRouter()


@router_client.get("/page", summary="获得OAuth2客户端分页")
async def get_oauth2_client_page(
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    name: str = Query(None, description="应用名"),
    status: int = Query(None, description="状态"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:oauth2-client:query")),
):
    """分页查询OAuth2客户端"""
    clients, total = await OAuth2ClientService.get_page(
        db, page_no, page_size, name, status
    )
    return page_success(
        list_data=[
            {
                "id": c.id,
                "clientId": c.client_id,
                "secret": c.secret,
                "name": c.name,
                "logo": c.logo,
                "description": c.description,
                "status": c.status,
                "accessTokenValiditySeconds": c.access_token_validity_seconds,
                "refreshTokenValiditySeconds": c.refresh_token_validity_seconds,
                "redirectUris": c.redirect_uris,
                "authorizedGrantTypes": c.authorized_grant_types,
                "scopes": c.scopes,
                "autoApproveScopes": c.auto_approve_scopes,
                "authorities": c.authorities,
                "resourceIds": c.resource_ids,
                "additionalInformation": c.additional_information,
                "createTime": c.create_time,
            }
            for c in clients
        ],
        total=total,
        page_no=page_no,
        page_size=page_size,
    )


@router_client.get("/get", summary="获得OAuth2客户端")
async def get_oauth2_client(
    id: int = Query(..., description="客户端编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:oauth2-client:query")),
):
    """根据ID获取OAuth2客户端详情"""
    client = await OAuth2ClientService.get_by_id(db, id)
    if not client:
        return success(data=None)
    return success(data={
        "id": client.id,
        "clientId": client.client_id,
        "secret": client.secret,
        "name": client.name,
        "logo": client.logo,
        "description": client.description,
        "status": client.status,
        "accessTokenValiditySeconds": client.access_token_validity_seconds,
        "refreshTokenValiditySeconds": client.refresh_token_validity_seconds,
        "redirectUris": client.redirect_uris,
        "authorizedGrantTypes": client.authorized_grant_types,
        "scopes": client.scopes,
        "autoApproveScopes": client.auto_approve_scopes,
        "authorities": client.authorities,
        "resourceIds": client.resource_ids,
        "additionalInformation": client.additional_information,
        "createTime": client.create_time,
    })


@router_token.get("/page", summary="获得访问令牌分页")
async def get_oauth2_token_page(
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    user_id: int = Query(None, description="用户编号"),
    user_type: int = Query(None, description="用户类型"),
    client_id: str = Query(None, description="客户端编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:oauth2-token:page")),
):
    """分页查询访问令牌，只返回有效期内的"""
    tokens, total = await OAuth2AccessTokenService.get_page(
        db, page_no, page_size, user_id, user_type, client_id
    )
    return page_success(
        list_data=[
            {
                "id": t.id,
                "accessToken": t.access_token,
                "refreshToken": t.refresh_token,
                "userId": t.user_id,
                "userType": t.user_type,
                "userInfo": t.user_info,
                "clientId": t.client_id,
                "scopes": t.scopes,
                "expiresTime": t.expires_time,
                "createTime": t.create_time,
            }
            for t in tokens
        ],
        total=total,
        page_no=page_no,
        page_size=page_size,
    )