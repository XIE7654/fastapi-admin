"""
邮件控制器
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.module.system.model.user import User
from app.module.system.service.mail import MailAccountService, MailTemplateService, MailLogService
from app.common.response import success, page_success

# 邮箱账号路由
router_account = APIRouter()

# 邮件模板路由
router_template = APIRouter()

# 邮件日志路由
router_log = APIRouter()


# ==================== 邮箱账号接口 ====================

@router_account.get("/page", summary="获得邮箱账号分页")
async def get_mail_account_page(
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    mail: str = Query(None, description="邮箱"),
    username: str = Query(None, description="用户名"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:mail-account:query")),
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

@router_template.get("/page", summary="获得邮件模板分页")
async def get_mail_template_page(
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    name: str = Query(None, description="模板名称"),
    code: str = Query(None, description="模板编码"),
    account_id: int = Query(None, description="邮箱账号编号"),
    status: int = Query(None, description="状态"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:mail-template:query")),
):
    """分页查询邮件模板"""
    templates, total = await MailTemplateService.get_page(
        db, page_no, page_size, name, code, account_id, status
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
    # _: User = Depends(check_permission("system:mail-log:query")),
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