"""
日志控制器
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import check_permission
from app.module.system.model.user import User
from app.module.system.service.operate_log import OperateLogService
from app.module.system.service.login_log import LoginLogService
from app.module.system.schema.log import (
    OperateLogPageQuery,
    OperateLogResponse,
    LoginLogPageQuery,
    LoginLogResponse,
)
from app.common.response import success, page_success
from app.common.excel import ExcelUtils

# 操作日志路由
router_operate = APIRouter()

# 登录日志路由
router_login = APIRouter()

# 用户类型字典
USER_TYPE_DICT = {1: "管理员", 2: "会员"}

# 日志类型字典
LOG_TYPE_DICT = {100: "登录", 101: "登出"}

# 登录结果字典
LOGIN_RESULT_DICT = {0: "成功", 10: "账号或密码不正确", 20: "账号被禁用", 30: "验证码不存在", 31: "验证码不正确"}


# ==================== 操作日志 ====================

@router_operate.get("/page", summary="获取操作日志分页列表")
async def get_operate_log_page(
    query: OperateLogPageQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:operate-log:query")),
):
    """分页查询操作日志"""
    logs, total = await OperateLogService.get_list(db, query)
    return page_success(
        list_data=[OperateLogResponse.model_validate(log) for log in logs],
        total=total,
        page_no=query.page_no,
        page_size=query.page_size,
    )


@router_operate.get("/get", summary="查看操作日志")
async def get_operate_log(
    id: int = Query(..., description="日志编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:operate-log:query")),
):
    """根据ID获取操作日志详情"""
    from app.module.system.model.operate_log import OperateLog
    result = await db.execute(
        select(OperateLog, User.nickname)
        .outerjoin(User, OperateLog.user_id == User.id)
        .where(OperateLog.id == id, OperateLog.deleted == 0)
    )
    row = result.first()
    if not row:
        return success(data=None)
    log, user_name = row
    log_dict = {
        "id": log.id,
        "trace_id": log.trace_id,
        "user_id": log.user_id,
        "user_name": user_name,
        "user_type": log.user_type,
        "type": log.type,
        "sub_type": log.sub_type,
        "biz_id": log.biz_id,
        "action": log.action,
        "extra": log.extra,
        "request_method": log.request_method,
        "request_url": log.request_url,
        "user_ip": log.user_ip,
        "user_agent": log.user_agent,
        "create_time": log.create_time,
    }
    return success(data=OperateLogResponse.model_validate(log_dict))


# ==================== 登录日志 ====================

@router_login.get("/page", summary="获取登录日志分页列表")
async def get_login_log_page(
    query: LoginLogPageQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:login-log:query")),
):
    """分页查询登录日志"""
    logs, total = await LoginLogService.get_list(db, query)
    return page_success(
        list_data=[LoginLogResponse.model_validate(log) for log in logs],
        total=total,
        page_no=query.page_no,
        page_size=query.page_size,
    )


@router_login.get("/get", summary="获得登录日志")
async def get_login_log(
    id: int = Query(..., description="日志编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:login-log:query")),
):
    """根据ID获取登录日志详情"""
    from app.module.system.model.login_log import LoginLog
    result = await db.execute(
        select(LoginLog).where(LoginLog.id == id, LoginLog.deleted == 0)
    )
    log = result.scalar_one_or_none()
    if not log:
        return success(data=None)
    return success(data=LoginLogResponse.model_validate(log))


@router_operate.get("/export-excel", summary="导出操作日志 Excel")
async def export_operate_log_excel(
    user_id: Optional[int] = Query(None, alias="userId", description="用户编号"),
    type: Optional[str] = Query(None, description="操作模块"),
    sub_type: Optional[str] = Query(None, alias="subType", description="操作名"),
    create_time: List[datetime] = Query(None, alias="createTime", description="操作时间"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:operate-log:export")),
):
    """导出操作日志 Excel"""
    # 获取数据
    logs = await OperateLogService.get_export_list(
        db, user_id=user_id, type=type, sub_type=sub_type, create_time=create_time
    )

    # 定义表头和字段
    headers = ["日志编号", "链路追踪编号", "用户编号", "用户名称", "用户类型", "操作模块", "操作名", "操作业务编号", "操作内容", "拓展字段", "请求方法", "请求地址", "用户 IP", "浏览器 UA", "创建时间"]
    fields = ["id", "trace_id", "user_id", "user_name", "user_type", "type", "sub_type", "biz_id", "action", "extra", "request_method", "request_url", "user_ip", "user_agent", "create_time"]

    # 定义转换器
    converters = {
        "user_type": lambda v: USER_TYPE_DICT.get(v, v),
    }

    # 导出 Excel
    return ExcelUtils.export_excel(
        data=logs,
        headers=headers,
        fields=fields,
        filename="操作日志.xlsx",
        sheet_name="操作日志",
        converters=converters,
    )


@router_login.get("/export-excel", summary="导出登录日志 Excel")
async def export_login_log_excel(
    user_id: Optional[int] = Query(None, alias="userId", description="用户编号"),
    username: Optional[str] = Query(None, description="用户账号"),
    log_type: Optional[int] = Query(None, alias="logType", description="日志类型"),
    result: Optional[int] = Query(None, description="登录结果"),
    user_ip: Optional[str] = Query(None, alias="userIp", description="用户 IP"),
    create_time: List[datetime] = Query(None, alias="createTime", description="登录时间"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:login-log:export")),
):
    """导出登录日志 Excel"""
    # 获取数据
    logs = await LoginLogService.get_export_list(
        db, user_id=user_id, username=username, log_type=log_type, result=result, user_ip=user_ip, create_time=create_time
    )

    # 定义表头和字段
    headers = ["日志编号", "链路追踪编号", "用户编号", "用户账号", "日志类型", "登录结果", "登录 IP", "浏览器 UA", "登录时间"]
    fields = ["id", "trace_id", "user_id", "username", "log_type", "result", "user_ip", "user_agent", "create_time"]

    # 定义转换器
    converters = {
        "log_type": lambda v: LOG_TYPE_DICT.get(v, v),
        "result": lambda v: LOGIN_RESULT_DICT.get(v, v),
    }

    # 导出 Excel
    return ExcelUtils.export_excel(
        data=logs,
        headers=headers,
        fields=fields,
        filename="登录日志.xlsx",
        sheet_name="登录日志",
        converters=converters,
    )