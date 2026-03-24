"""
邮件控制器
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, Body
from pydantic import Field, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.module.system.model.user import User
from app.module.system.service.mail import MailAccountService, MailTemplateService, MailLogService
from app.common.response import success, page_success
from app.common.schema import CamelModel


# ==================== 请求 Schema ====================

class MailAccountCreateReq(CamelModel):
    """邮箱账号创建请求"""

    mail: str = Field(..., description="邮箱")
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    host: str = Field(..., description="SMTP服务器域名")
    port: int = Field(..., description="SMTP服务器端口")
    ssl_enable: bool = Field(default=False, description="是否开启SSL")
    starttls_enable: bool = Field(default=False, description="是否开启STARTTLS")


class MailAccountUpdateReq(CamelModel):
    """邮箱账号更新请求"""

    id: int = Field(..., description="编号")
    mail: Optional[str] = Field(None, description="邮箱")
    username: Optional[str] = Field(None, description="用户名")
    password: Optional[str] = Field(None, description="密码")
    host: Optional[str] = Field(None, description="SMTP服务器域名")
    port: Optional[int] = Field(None, description="SMTP服务器端口")
    ssl_enable: Optional[bool] = Field(None, description="是否开启SSL")
    starttls_enable: Optional[bool] = Field(None, description="是否开启STARTTLS")


class MailTemplateCreateReq(CamelModel):
    """邮件模板创建请求"""

    name: str = Field(..., description="模板名称")
    code: str = Field(..., description="模板编码")
    account_id: int = Field(..., description="发送的邮箱账号编号")
    nickname: Optional[str] = Field(None, description="发送人名称")
    title: str = Field(..., description="模板标题")
    content: str = Field(..., description="模板内容")
    status: int = Field(..., description="状态")
    remark: Optional[str] = Field(None, description="备注")


class MailTemplateUpdateReq(CamelModel):
    """邮件模板更新请求"""

    id: int = Field(..., description="模板编号")
    name: Optional[str] = Field(None, description="模板名称")
    code: Optional[str] = Field(None, description="模板编码")
    account_id: Optional[int] = Field(None, description="发送的邮箱账号编号")
    nickname: Optional[str] = Field(None, description="发送人名称")
    title: Optional[str] = Field(None, description="模板标题")
    content: Optional[str] = Field(None, description="模板内容")
    status: Optional[int] = Field(None, description="状态")
    remark: Optional[str] = Field(None, description="备注")


# 邮箱账号路由
router_account = APIRouter()

# 邮件模板路由
router_template = APIRouter()

# 邮件日志路由
router_log = APIRouter()


# ==================== 邮箱账号接口 ====================

@router_account.post("/create", summary="创建邮箱账号")
async def create_mail_account(
    req: MailAccountCreateReq,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:mail-account:create")),
):
    """创建邮箱账号"""
    account = await MailAccountService.create(
        db=db,
        mail=req.mail,
        username=req.username,
        password=req.password,
        host=req.host,
        port=req.port,
        ssl_enable=req.ssl_enable,
        starttls_enable=req.starttls_enable,
    )
    return success(data=account.id)


@router_account.put("/update", summary="修改邮箱账号")
async def update_mail_account(
    req: MailAccountUpdateReq,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:mail-account:update")),
):
    """修改邮箱账号"""
    await MailAccountService.update(
        db=db,
        account_id=req.id,
        mail=req.mail,
        username=req.username,
        password=req.password,
        host=req.host,
        port=req.port,
        ssl_enable=req.ssl_enable,
        starttls_enable=req.starttls_enable,
    )
    return success(data=True)


@router_account.delete("/delete", summary="删除邮箱账号")
async def delete_mail_account(
    id: int = Query(..., description="账号编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:mail-account:delete")),
):
    """删除邮箱账号"""
    await MailAccountService.delete(db, id)
    return success(data=True)


@router_account.delete("/delete-list", summary="批量删除邮箱账号")
async def delete_mail_account_list(
    ids: List[int] = Query(..., description="账号编号列表"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:mail-account:delete")),
):
    """批量删除邮箱账号"""
    count = await MailAccountService.delete_by_ids(db, ids)
    return success(data=True)


@router_account.get("/page", summary="获得邮箱账号分页")
async def get_mail_account_page(
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    mail: str = Query(None, description="邮箱"),
    username: str = Query(None, description="用户名"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:mail-account:query")),
):
    """分页查询邮箱账号"""
    accounts, total = await MailAccountService.get_page(
        db, page_no, page_size, mail, username
    )
    return page_success(
        list_data=[
            {
                "id": a.id,
                "mail": a.mail,
                "username": a.username,
                "host": a.host,
                "port": a.port,
                "sslEnable": a.ssl_enable == 1,
                "starttlsEnable": a.starttls_enable == 1,
                "createTime": a.create_time,
            }
            for a in accounts
        ],
        total=total,
        page_no=page_no,
        page_size=page_size,
    )


@router_account.get("/simple-list", summary="获得邮箱账号精简列表")
async def get_simple_mail_account_list(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取邮箱账号精简列表"""
    accounts = await MailAccountService.get_all(db)
    return success(data=[
        {
            "id": a.id,
            "mail": a.mail,
        }
        for a in accounts
    ])


@router_account.get("/list-all-simple", summary="获得邮箱账号精简列表")
async def get_list_all_simple(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取邮箱账号精简列表（兼容路径）"""
    accounts = await MailAccountService.get_all(db)
    return success(data=[
        {
            "id": a.id,
            "mail": a.mail,
        }
        for a in accounts
    ])


@router_account.get("/get", summary="获得邮箱账号")
async def get_mail_account(
    id: int = Query(..., description="账号编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:mail-account:query")),
):
    """根据ID获取邮箱账号详情"""
    account = await MailAccountService.get_by_id(db, id)
    if not account:
        return success(data=None)
    return success(data={
        "id": account.id,
        "mail": account.mail,
        "username": account.username,
        "password": account.password,
        "host": account.host,
        "port": account.port,
        "sslEnable": account.ssl_enable == 1,
        "starttlsEnable": account.starttls_enable == 1,
        "createTime": account.create_time,
    })


# ==================== 邮件模板接口 ====================

@router_template.post("/create", summary="创建邮件模板")
async def create_mail_template(
    req: MailTemplateCreateReq,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:mail-template:create")),
):
    """创建邮件模板"""
    template_id = await MailTemplateService.create(
        db=db,
        name=req.name,
        code=req.code,
        account_id=req.account_id,
        nickname=req.nickname,
        title=req.title,
        content=req.content,
        status=req.status,
        remark=req.remark,
    )
    return success(data=template_id)


@router_template.put("/update", summary="修改邮件模板")
async def update_mail_template(
    req: MailTemplateUpdateReq,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:mail-template:update")),
):
    """修改邮件模板"""
    await MailTemplateService.update(
        db=db,
        template_id=req.id,
        name=req.name,
        code=req.code,
        account_id=req.account_id,
        nickname=req.nickname,
        title=req.title,
        content=req.content,
        status=req.status,
        remark=req.remark,
    )
    return success(data=True)


@router_template.delete("/delete", summary="删除邮件模板")
async def delete_mail_template(
    id: int = Query(..., description="模板编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:mail-template:delete")),
):
    """删除邮件模板"""
    await MailTemplateService.delete(db, id)
    return success(data=True)


@router_template.delete("/delete-list", summary="批量删除邮件模板")
async def delete_mail_template_list(
    ids: List[int] = Query(..., description="模板编号列表"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:mail-template:delete")),
):
    """批量删除邮件模板"""
    count = await MailTemplateService.delete_list(db, ids)
    return success(data=count)


@router_template.get("/page", summary="获得邮件模板分页")
async def get_mail_template_page(
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    name: str = Query(None, description="模板名称"),
    code: str = Query(None, description="模板编码"),
    account_id: int = Query(None, description="邮箱账号编号"),
    status: int = Query(None, description="状态"),
    create_time: Optional[List[datetime]] = Query(None, description="创建时间范围"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:mail-template:query")),
):
    """分页查询邮件模板"""
    templates, total = await MailTemplateService.get_page(
        db, page_no, page_size, name, code, account_id, status, create_time
    )
    return page_success(
        list_data=[
            {
                "id": t.id,
                "name": t.name,
                "code": t.code,
                "accountId": t.account_id,
                "nickname": t.nickname,
                "title": t.title,
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


@router_template.get("/simple-list", summary="获得邮件模板精简列表")
async def get_simple_mail_template_list(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取邮件模板精简列表"""
    templates = await MailTemplateService.get_all(db)
    return success(data=[
        {
            "id": t.id,
            "name": t.name,
            "code": t.code,
            "accountId": t.account_id,
        }
        for t in templates
    ])


@router_template.get("/list-all-simple", summary="获得邮件模板精简列表")
async def get_template_list_all_simple(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取邮件模板精简列表（兼容路径）"""
    templates = await MailTemplateService.get_all(db)
    return success(data=[
        {
            "id": t.id,
            "name": t.name,
            "code": t.code,
            "accountId": t.account_id,
        }
        for t in templates
    ])


@router_template.get("/get", summary="获得邮件模板")
async def get_mail_template(
    id: int = Query(..., description="模板编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:mail-template:query")),
):
    """根据ID获取邮件模板详情"""
    template = await MailTemplateService.get_by_id(db, id)
    if not template:
        return success(data=None)
    return success(data={
        "id": template.id,
        "name": template.name,
        "code": template.code,
        "accountId": template.account_id,
        "nickname": template.nickname,
        "title": template.title,
        "content": template.content,
        "params": template.params,
        "status": template.status,
        "remark": template.remark,
        "createTime": template.create_time,
    })


# ==================== 邮件日志接口 ====================

@router_log.get("/page", summary="获得邮件日志分页")
async def get_mail_log_page(
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    user_id: int = Query(None, description="用户编号"),
    user_type: int = Query(None, description="用户类型"),
    to_mails: str = Query(None, description="接收邮箱"),
    account_id: int = Query(None, description="邮箱账号编号"),
    template_id: int = Query(None, description="模板编号"),
    send_status: int = Query(None, description="发送状态"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:mail-log:query")),
):
    """分页查询邮件日志"""
    logs, total = await MailLogService.get_page(
        db, page_no, page_size, user_id, user_type, to_mails,
        account_id, template_id, send_status
    )
    return page_success(
        list_data=[
            {
                "id": log.id,
                "userId": log.user_id,
                "userType": log.user_type,
                "toMails": log.to_mails,
                "ccMails": log.cc_mails,
                "bccMails": log.bcc_mails,
                "accountId": log.account_id,
                "fromMail": log.from_mail,
                "templateId": log.template_id,
                "templateCode": log.template_code,
                "templateNickname": log.template_nickname,
                "templateTitle": log.template_title,
                "templateContent": log.template_content,
                "templateParams": log.template_params,
                "sendStatus": log.send_status,
                "sendTime": log.send_time,
                "sendMessageId": log.send_message_id,
                "sendException": log.send_exception,
                "createTime": log.create_time,
            }
            for log in logs
        ],
        total=total,
        page_no=page_no,
        page_size=page_size,
    )


@router_log.get("/get", summary="获得邮件日志")
async def get_mail_log(
    id: int = Query(..., description="日志编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:mail-log:query")),
):
    """根据ID获取邮件日志详情"""
    log = await MailLogService.get_by_id(db, id)
    if not log:
        return success(data=None)
    return success(data={
        "id": log.id,
        "userId": log.user_id,
        "userType": log.user_type,
        "toMails": log.to_mails,
        "ccMails": log.cc_mails,
        "bccMails": log.bcc_mails,
        "accountId": log.account_id,
        "fromMail": log.from_mail,
        "templateId": log.template_id,
        "templateCode": log.template_code,
        "templateNickname": log.template_nickname,
        "templateTitle": log.template_title,
        "templateContent": log.template_content,
        "templateParams": log.template_params,
        "sendStatus": log.send_status,
        "sendTime": log.send_time,
        "sendMessageId": log.send_message_id,
        "sendException": log.send_exception,
        "createTime": log.create_time,
    })