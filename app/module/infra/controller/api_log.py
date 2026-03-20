"""
API 日志控制器
"""
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.module.system.model.user import User
from app.module.infra.service.api_log import ApiAccessLogService, ApiErrorLogService
from app.common.response import success, page_success

router = APIRouter()


# API 访问日志
access_router = APIRouter()


@access_router.get("/page", summary="获得API访问日志分页")
async def get_api_access_log_page(
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    user_id: int = Query(None, description="用户ID"),
    application_name: str = Query(None, description="应用名"),
    request_url: str = Query(None, description="请求地址"),
    begin_time: datetime = Query(None, description="开始时间"),
    end_time: datetime = Query(None, description="结束时间"),
    result_code: int = Query(None, description="结果码"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("infra:api-access-log:query")),
):
    """分页查询API访问日志"""
    logs, total = await ApiAccessLogService.get_page(
        db, page_no, page_size, user_id, application_name, request_url,
        begin_time, end_time, result_code
    )
    return page_success(
        list_data=[
            {
                "id": l.id,
                "traceId": l.trace_id,
                "userId": l.user_id,
                "userType": l.user_type,
                "applicationName": l.application_name,
                "requestMethod": l.request_method,
                "requestUrl": l.request_url,
                "requestParams": l.request_params,
                "responseBody": l.response_body,
                "userIp": l.user_ip,
                "userAgent": l.user_agent,
                "operateModule": l.operate_module,
                "operateName": l.operate_name,
                "operateType": l.operate_type,
                "beginTime": l.begin_time,
                "endTime": l.end_time,
                "duration": l.duration,
                "resultCode": l.result_code,
                "resultMsg": l.result_msg,
                "createTime": l.create_time,
            }
            for l in logs
        ],
        total=total,
        page_no=page_no,
        page_size=page_size,
    )


# API 异常日志
error_router = APIRouter()


@error_router.get("/page", summary="获得API异常日志分页")
async def get_api_error_log_page(
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    user_id: int = Query(None, description="用户ID"),
    application_name: str = Query(None, description="应用名"),
    request_url: str = Query(None, description="请求地址"),
    exception_time: datetime = Query(None, description="异常时间"),
    process_status: int = Query(None, description="处理状态"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("infra:api-error-log:query")),
):
    """分页查询API异常日志"""
    logs, total = await ApiErrorLogService.get_page(
        db, page_no, page_size, user_id, application_name, request_url,
        exception_time, process_status
    )
    return page_success(
        list_data=[
            {
                "id": l.id,
                "traceId": l.trace_id,
                "userId": l.user_id,
                "userType": l.user_type,
                "applicationName": l.application_name,
                "requestMethod": l.request_method,
                "requestUrl": l.request_url,
                "requestParams": l.request_params,
                "userIp": l.user_ip,
                "userAgent": l.user_agent,
                "exceptionTime": l.exception_time,
                "exceptionName": l.exception_name,
                "exceptionMessage": l.exception_message,
                "processStatus": l.process_status,
                "processTime": l.process_time,
                "createTime": l.create_time,
            }
            for l in logs
        ],
        total=total,
        page_no=page_no,
        page_size=page_size,
    )


@error_router.put("/update-status", summary="更新异常日志处理状态")
async def update_error_log_status(
    id: int = Query(..., description="日志ID"),
    process_status: int = Query(..., description="处理状态"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("infra:api-error-log:update-status")),
):
    """更新异常日志处理状态"""
    await ApiErrorLogService.update_status(db, id, process_status)
    return success(data=True)