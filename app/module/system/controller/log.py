"""
日志控制器
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
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
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    user_id: int = Query(None, description="用户编号"),
    type: str = Query(None, description="操作模块类型"),
    sub_type: str = Query(None, description="操作名"),
    create_time: List[str] = Query(None, description="创建时间范围"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:operate-log:query")),
):
    """分页查询操作日志"""
    query = OperateLogPageQuery(
        page_no=page_no,
        page_size=page_size,
        user_id=user_id,
        type=type,
        sub_type=sub_type,
        create_time=create_time,
    )
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
        select(OperateLog).where(OperateLog.id == id, OperateLog.deleted == 0)
    )
    log = result.scalar_one_or_none()
    if not log:
        return success(data=None)
    return success(data=OperateLogResponse.model_validate(log))


# ==================== 登录日志 ====================

@router_login.get("/page", summary="获取登录日志分页列表")
async def get_login_log_page(
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    user_id: int = Query(None, description="用户编号"),
    username: str = Query(None, description="用户名"),
    log_type: int = Query(None, description="日志类型"),
    result: int = Query(None, description="结果码"),
    user_ip: str = Query(None, description="用户IP"),
    create_time: List[str] = Query(None, description="登录时间范围"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("system:login-log:query")),
):
    """分页查询登录日志"""
    query = LoginLogPageQuery(
        page_no=page_no,
        page_size=page_size,
        user_id=user_id,
        username=username,
        log_type=log_type,
        result=result,
        user_ip=user_ip,
        create_time=create_time,
    )
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