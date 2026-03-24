"""
短信日志控制器
"""
import io
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import check_permission
from app.module.system.model.user import User
from app.module.system.service.sms_log import SmsLogService
from app.common.response import success, page_success
from app.common.excel import ExcelUtils

router = APIRouter()


# 短信类型字典
SMS_TEMPLATE_TYPE_DICT = {1: "验证码", 2: "通知", 3: "营销"}

# 用户类型字典
USER_TYPE_DICT = {1: "管理员", 2: "会员"}

# 发送状态字典
SMS_SEND_STATUS_DICT = {0: "发送中", 10: "发送成功", 20: "发送失败", 30: "不发送"}

# 接收状态字典
SMS_RECEIVE_STATUS_DICT = {0: "等待接收", 10: "接收成功", 20: "接收失败"}


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
    _: User = Depends(check_permission("system:sms-log:query")),
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
                "apiTemplateId": log.api_template_id,
                "mobile": log.mobile,
                "userId": log.user_id,
                "userType": log.user_type,
                "sendStatus": log.send_status,
                "sendTime": log.send_time,
                "apiSendCode": log.api_send_code,
                "apiSendMsg": log.api_send_msg,
                "apiRequestId": log.api_request_id,
                "apiSerialNo": log.api_serial_no,
                "receiveStatus": log.receive_status,
                "receiveTime": log.receive_time,
                "apiReceiveCode": log.api_receive_code,
                "apiReceiveMsg": log.api_receive_msg,
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
    _: User = Depends(check_permission("system:sms-log:query")),
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
        "apiTemplateId": log.api_template_id,
        "mobile": log.mobile,
        "userId": log.user_id,
        "userType": log.user_type,
        "sendStatus": log.send_status,
        "sendTime": log.send_time,
        "apiSendCode": log.api_send_code,
        "apiSendMsg": log.api_send_msg,
        "apiRequestId": log.api_request_id,
        "apiSerialNo": log.api_serial_no,
        "receiveStatus": log.receive_status,
        "receiveTime": log.receive_time,
        "apiReceiveCode": log.api_receive_code,
        "apiReceiveMsg": log.api_receive_msg,
        "createTime": log.create_time,
    })


@router.get("/export-excel", summary="导出短信日志 Excel")
async def export_sms_log_excel(
    channel_id: int = Query(None, alias="channelId", description="渠道编号"),
    template_id: int = Query(None, alias="templateId", description="模板编号"),
    mobile: str = Query(None, description="手机号"),
    send_status: int = Query(None, alias="sendStatus", description="发送状态"),
    receive_status: int = Query(None, alias="receiveStatus", description="接收状态"),
    send_time: List[datetime] = Query(None, alias="sendTime", description="发送时间"),
    receive_time: List[datetime] = Query(None, alias="receiveTime", description="接收时间"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:sms-log:export")),
):
    """导出短信日志 Excel"""
    # 获取数据
    logs = await SmsLogService.get_list(
        db,
        channel_id=channel_id,
        template_id=template_id,
        mobile=mobile,
        send_status=send_status,
        receive_status=receive_status,
        send_time=send_time,
        receive_time=receive_time,
    )

    # 定义表头和字段
    headers = [
        "编号", "短信渠道编号", "短信渠道编码", "模板编号", "模板编码",
        "短信类型", "短信内容", "短信参数", "短信API的模板编号",
        "手机号", "用户编号", "用户类型", "发送状态", "发送时间",
        "短信API发送结果的编码", "短信API发送失败的提示", "短信API发送返回的唯一请求ID",
        "短信API发送返回的序号", "接收状态", "接收时间",
        "API接收结果的编码", "API接收结果的说明", "创建时间"
    ]
    fields = [
        "id", "channel_id", "channel_code", "template_id", "template_code",
        "template_type", "template_content", "template_params", "api_template_id",
        "mobile", "user_id", "user_type", "send_status", "send_time",
        "api_send_code", "api_send_msg", "api_request_id",
        "api_serial_no", "receive_status", "receive_time",
        "api_receive_code", "api_receive_msg", "create_time"
    ]

    # 定义转换器
    converters = {
        "template_type": lambda v: SMS_TEMPLATE_TYPE_DICT.get(v, v),
        "user_type": lambda v: USER_TYPE_DICT.get(v, v) if v else None,
        "send_status": lambda v: SMS_SEND_STATUS_DICT.get(v, v),
        "receive_status": lambda v: SMS_RECEIVE_STATUS_DICT.get(v, v),
    }

    # 导出 Excel
    return ExcelUtils.export_excel(
        data=logs,
        headers=headers,
        fields=fields,
        filename="短信日志.xlsx",
        sheet_name="短信日志",
        converters=converters,
    )