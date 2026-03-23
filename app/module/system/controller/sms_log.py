"""
短信日志控制器
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.module.system.service.sms_log import SmsLogService
from app.common.response import success, page_success

router = APIRouter()


@router.get("/page", summary="获得短信日志分页")
async def get_sms_log_page(
    page_no: int = Query(1, ge=1, alias="pageNo", description="页码"),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize", description="每页数量"),
    channel_id: int = Query(None, alias="channelId", description="渠道编号"),
    template_id: int = Query(None, alias="templateId", description="模板编号"),
    mobile: str = Query(None, description="手机号"),
    send_status: int = Query(None, alias="sendStatus", description="发送状态"),
    receive_status: int = Query(None, alias="receiveStatus", description="接收状态"),
    send_time: List[datetime] = Query(None, alias="sendTime", description="发送时间"),
    receive_time: List[datetime] = Query(None, alias="receiveTime", description="接收时间"),
    db: AsyncSession = Depends(get_db),
):
    """分页查询短信日志"""
    logs, total = await SmsLogService.get_page(
        db,
        page_no=page_no,
        page_size=page_size,
        channel_id=channel_id,
        template_id=template_id,
        mobile=mobile,
        send_status=send_status,
        receive_status=receive_status,
        send_time=send_time,
        receive_time=receive_time,
    )
    return page_success(
        list_data=[
            {
                "id": log.id,
                "channelId": log.channel_id,
                "channelCode": log.channel_code,
                "templateId": log.template_id,
                "templateCode": log.template_code,
                "templateType": log.template_type,
                "templateContent": log.template_content,
                "templateParams": log.template_params,
                "mobile": log.mobile,
                "userId": log.user_id,
                "userType": log.user_type,
                "sendStatus": log.send_status,
                "sendTime": log.send_time,
                "apiCode": log.api_code,
                "apiMsg": log.api_msg,
                "apiRequestId": log.api_request_id,
                "receiveStatus": log.receive_status,
                "receiveTime": log.receive_time,
                "createTime": log.create_time,
            }
            for log in logs
        ],
        total=total,
        page_no=page_no,
        page_size=page_size,
    )


@router.get("/get", summary="获得短信日志")
async def get_sms_log(
    id: int = Query(..., description="日志编号"),
    db: AsyncSession = Depends(get_db),
):
    """根据ID获取短信日志详情"""
    log = await SmsLogService.get_by_id(db, id)
    if not log:
        return success(data=None)
    return success(data={
        "id": log.id,
        "channelId": log.channel_id,
        "channelCode": log.channel_code,
        "templateId": log.template_id,
        "templateCode": log.template_code,
        "templateType": log.template_type,
        "templateContent": log.template_content,
        "templateParams": log.template_params,
        "mobile": log.mobile,
        "userId": log.user_id,
        "userType": log.user_type,
        "sendStatus": log.send_status,
        "sendTime": log.send_time,
        "apiCode": log.api_code,
        "apiMsg": log.api_msg,
        "apiRequestId": log.api_request_id,
        "receiveStatus": log.receive_status,
        "receiveTime": log.receive_time,
        "createTime": log.create_time,
    })