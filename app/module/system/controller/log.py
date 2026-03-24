"""
日志控制器
"""
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

# 操作日志路由
router_operate = APIRouter()

# 登录日志路由
router_login = APIRouter()


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