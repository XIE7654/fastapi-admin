"""
短信控制器
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.module.system.model.user import User
from app.module.system.service.sms import SmsChannelService, SmsTemplateService
from app.common.response import success, page_success

# 短信渠道路由
router_channel = APIRouter()

# 短信模板路由
router_template = APIRouter()


# ==================== 短信渠道接口 ====================

@router_channel.get("/page", summary="获得短信渠道分页")
async def get_sms_channel_page(
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: int = Query(None, description="状态"),
    signature: str = Query(None, description="短信签名"),
    code: str = Query(None, description="渠道编码"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:sms-channel:query")),
):
    """分页查询短信渠道"""
    channels, total = await SmsChannelService.get_page(
        db, page_no, page_size, status, signature, code
    )
    return page_success(
        list_data=[
            {
                "id": c.id,
                "signature": c.signature,
                "code": c.code,
                "status": c.status,
                "remark": c.remark,
                "apiKey": c.api_key,
                "apiSecret": c.api_secret,
                "callbackUrl": c.callback_url,
                "createTime": c.create_time,
            }
            for c in channels
        ],
        total=total,
        page_no=page_no,
        page_size=page_size,
    )


@router_channel.get("/simple-list", summary="获得短信渠道精简列表")
async def get_simple_sms_channel_list(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取短信渠道精简列表，包含被禁用的短信渠道"""
    channels = await SmsChannelService.get_all(db)
    return success(data=[
        {
            "id": c.id,
            "code": c.code,
            "signature": c.signature,
        }
        for c in channels
    ])


@router_channel.get("/list-all-simple", summary="获得短信渠道精简列表")
async def get_list_all_simple(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取短信渠道精简列表（兼容路径）"""
    channels = await SmsChannelService.get_all(db)
    return success(data=[
        {
            "id": c.id,
            "code": c.code,
            "signature": c.signature,
        }
        for c in channels
    ])


@router_channel.get("/get", summary="获得短信渠道")
async def get_sms_channel(
    id: int = Query(..., description="渠道编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:sms-channel:query")),
):
    """根据ID获取短信渠道详情"""
    channel = await SmsChannelService.get_by_id(db, id)
    if not channel:
        return success(data=None)
    return success(data={
        "id": channel.id,
        "signature": channel.signature,
        "code": channel.code,
        "status": channel.status,
        "remark": channel.remark,
        "apiKey": channel.api_key,
        "apiSecret": channel.api_secret,
        "callbackUrl": channel.callback_url,
        "createTime": channel.create_time,
    })


# ==================== 短信模板接口 ====================

@router_template.get("/page", summary="获得短信模板分页")
async def get_sms_template_page(
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: int = Query(None, description="状态"),
    name: str = Query(None, description="模板名称"),
    code: str = Query(None, description="模板编码"),
    channel_id: int = Query(None, description="短信渠道编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:sms-template:query")),
):
    """分页查询短信模板"""
    templates, total = await SmsTemplateService.get_page(
        db, page_no, page_size, status, name, code, channel_id
    )
    return page_success(
        list_data=[
            {
                "id": t.id,
                "name": t.name,
                "code": t.code,
                "channelId": t.channel_id,
                "channelCode": t.channel_code,
                "content": t.content,
                "params": t.params,
                "status": t.status,
                "remark": t.remark,
                "createTime": t.create_time,
            }
            for t in templates
        ],
        total=total,
        page_no=page_no,
        page_size=page_size,
    )


@router_template.get("/get", summary="获得短信模板")
async def get_sms_template(
    id: int = Query(..., description="模板编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:sms-template:query")),
):
    """根据ID获取短信模板详情"""
    template = await SmsTemplateService.get_by_id(db, id)
    if not template:
        return success(data=None)
    return success(data={
        "id": template.id,
        "name": template.name,
        "code": template.code,
        "channelId": template.channel_id,
        "channelCode": template.channel_code,
        "content": template.content,
        "params": template.params,
        "status": template.status,
        "remark": template.remark,
        "createTime": template.create_time,
    })