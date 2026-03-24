"""
短信控制器
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from pydantic import Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.module.system.model.user import User
from app.module.system.service.sms import SmsChannelService, SmsTemplateService
from app.common.response import success, page_success
from app.common.schema import CamelModel
from app.common.excel import ExcelUtils


# ==================== 请求 Schema ====================

class SmsChannelCreateReq(CamelModel):
    """短信渠道创建请求"""

    signature: str = Field(..., description="短信签名")
    code: str = Field(..., description="渠道编码")
    status: int = Field(..., description="启用状态")
    api_key: str = Field(..., description="短信API的账号")
    remark: Optional[str] = Field(None, description="备注")
    api_secret: Optional[str] = Field(None, description="短信API的密钥")
    callback_url: Optional[str] = Field(None, description="短信发送回调URL")


class SmsChannelUpdateReq(CamelModel):
    """短信渠道更新请求"""

    id: int = Field(..., description="编号")
    signature: Optional[str] = Field(None, description="短信签名")
    code: Optional[str] = Field(None, description="渠道编码")
    status: Optional[int] = Field(None, description="启用状态")
    api_key: Optional[str] = Field(None, description="短信API的账号")
    remark: Optional[str] = Field(None, description="备注")
    api_secret: Optional[str] = Field(None, description="短信API的密钥")
    callback_url: Optional[str] = Field(None, description="短信发送回调URL")


class SmsTemplateCreateReq(CamelModel):
    """短信模板创建请求"""

    name: str = Field(..., description="模板名称")
    code: str = Field(..., description="模板编码")
    channel_id: int = Field(..., description="短信渠道编号")
    content: str = Field(..., description="模板内容")
    status: int = Field(..., description="启用状态")
    remark: Optional[str] = Field(None, description="备注")


# 短信渠道路由
router_channel = APIRouter()

# 短信模板路由
router_template = APIRouter()

# 状态字典
STATUS_DICT = {0: "开启", 1: "禁用"}


# ==================== 短信渠道接口 ====================

@router_channel.post("/create", summary="创建短信渠道")
async def create_sms_channel(
    req: SmsChannelCreateReq,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:sms-channel:create")),
):
    """创建短信渠道"""
    channel = await SmsChannelService.create(
        db=db,
        signature=req.signature,
        code=req.code,
        status=req.status,
        api_key=req.api_key,
        remark=req.remark,
        api_secret=req.api_secret,
        callback_url=req.callback_url,
    )
    return success(data=channel.id)


@router_channel.put("/update", summary="更新短信渠道")
async def update_sms_channel(
    req: SmsChannelUpdateReq,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:sms-channel:update")),
):
    """更新短信渠道"""
    await SmsChannelService.update(
        db=db,
        channel_id=req.id,
        signature=req.signature,
        code=req.code,
        status=req.status,
        api_key=req.api_key,
        remark=req.remark,
        api_secret=req.api_secret,
        callback_url=req.callback_url,
    )
    return success(data=True)


@router_channel.delete("/delete", summary="删除短信渠道")
async def delete_sms_channel(
    id: int = Query(..., description="渠道编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:sms-channel:delete")),
):
    """删除短信渠道"""
    await SmsChannelService.delete(db, id)
    return success(data=True)


@router_channel.delete("/delete-list", summary="批量删除短信渠道")
async def delete_sms_channel_list(
    ids: List[int] = Query(..., description="渠道编号列表"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:sms-channel:delete")),
):
    """批量删除短信渠道"""
    count = await SmsChannelService.delete_by_ids(db, ids)
    return success(data=True)


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

@router_template.post("/create", summary="创建短信模板")
async def create_sms_template(
    req: SmsTemplateCreateReq,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:sms-template:create")),
):
    """创建短信模板"""
    template = await SmsTemplateService.create(
        db=db,
        name=req.name,
        code=req.code,
        channel_id=req.channel_id,
        content=req.content,
        status=req.status,
        remark=req.remark,
    )
    return success(data=template.id)


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


@router_template.get("/export-excel", summary="导出短信模板 Excel")
async def export_sms_template_excel(
    status: Optional[int] = Query(None, description="状态"),
    name: Optional[str] = Query(None, description="模板名称"),
    code: Optional[str] = Query(None, description="模板编码"),
    channel_id: Optional[int] = Query(None, alias="channelId", description="短信渠道编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:sms-template:export")),
):
    """导出短信模板 Excel"""
    # 获取数据
    templates = await SmsTemplateService.get_export_list(
        db, status=status, name=name, code=code, channel_id=channel_id
    )

    # 定义表头和字段
    headers = ["模板编号", "模板名称", "模板编码", "短信渠道编号", "短信渠道编码", "模板内容", "参数数组", "状态", "备注", "创建时间"]
    fields = ["id", "name", "code", "channel_id", "channel_code", "content", "params", "status", "remark", "create_time"]

    # 定义转换器
    converters = {
        "status": lambda v: STATUS_DICT.get(v, v),
    }

    # 导出 Excel
    return ExcelUtils.export_excel(
        data=templates,
        headers=headers,
        fields=fields,
        filename="短信模板.xlsx",
        sheet_name="短信模板",
        converters=converters,
    )