"""
日志控制器
"""
from typing import List
from fastapi import APIRouter, Depends, Query
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

router = APIRouter()


# ==================== 操作日志 ====================

@router.get("/operate-log/page", summary="获取操作日志分页列表")
async def get_operate_log_page(
    query: OperateLogPageQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:operate-log:list")),
):
    """分页查询操作日志"""
    logs, total = await OperateLogService.get_list(db, query)
    return page_success(
        list_data=[OperateLogResponse.model_validate(log) for log in logs],
        total=total,
        page_no=query.page_no,
        page_size=query.page_size,
    )


@router.delete("/operate-log/delete", summary="删除操作日志")
async def delete_operate_log(
    ids: List[int] = Query(..., description="日志ID列表"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:operate-log:delete")),
):
    """批量删除操作日志"""
    count = await OperateLogService.delete_by_ids(db, ids)
    return success(data={"count": count}, msg=f"成功删除 {count} 条日志")


# ==================== 登录日志 ====================

@router.get("/login-log/page", summary="获取登录日志分页列表")
async def get_login_log_page(
    query: LoginLogPageQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("system:login-log:list")),
):
    """分页查询登录日志"""
    logs, total = await LoginLogService.get_list(db, query)
    return page_success(
        list_data=[LoginLogResponse.model_validate(log) for log in logs],
        total=total,
        page_no=query.page_no,
        page_size=query.page_size,
    )