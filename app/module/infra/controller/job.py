"""
定时任务控制器
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.module.system.model.user import User
from app.module.infra.service.job import JobService, JobLogService
from app.common.response import success, page_success

router = APIRouter()


@router.get("/page", summary="获得定时任务分页")
async def get_job_page(
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    name: str = Query(None, description="任务名称"),
    status: int = Query(None, description="任务状态"),
    handler_name: str = Query(None, description="处理器名称"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("infra:job:query")),
):
    """分页查询定时任务"""
    jobs, total = await JobService.get_page(db, page_no, page_size, name, status, handler_name)
    return page_success(
        list_data=[
            {
                "id": j.id,
                "name": j.name,
                "status": j.status,
                "handlerName": j.handler_name,
                "handlerParam": j.handler_param,
                "cronExpression": j.cron_expression,
                "retryCount": j.retry_count,
                "retryInterval": j.retry_interval,
                "monitorTimeout": j.monitor_timeout,
                "createTime": j.create_time,
            }
            for j in jobs
        ],
        total=total,
        page_no=page_no,
        page_size=page_size,
    )


@router.get("/get", summary="获得定时任务")
async def get_job(
    id: int = Query(..., description="任务ID"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("infra:job:query")),
):
    """获取定时任务详情"""
    job = await JobService.get_by_id(db, id)
    if not job:
        return success(data=None)
    return success(data={
        "id": job.id,
        "name": job.name,
        "status": job.status,
        "handlerName": job.handler_name,
        "handlerParam": job.handler_param,
        "cronExpression": job.cron_expression,
        "retryCount": job.retry_count,
        "retryInterval": job.retry_interval,
        "monitorTimeout": job.monitor_timeout,
        "createTime": job.create_time,
    })


# 任务日志接口
log_router = APIRouter()


@log_router.get("/page", summary="获得任务日志分页")
async def get_job_log_page(
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    job_id: int = Query(None, description="任务ID"),
    handler_name: str = Query(None, description="处理器名称"),
    db: AsyncSession = Depends(get_db),
    # _: User = Depends(check_permission("infra:job:query")),
):
    """分页查询任务日志"""
    logs, total = await JobLogService.get_page(db, page_no, page_size, job_id, handler_name)
    return page_success(
        list_data=[
            {
                "id": l.id,
                "jobId": l.job_id,
                "handlerName": l.handler_name,
                "handlerParam": l.handler_param,
                "executeIndex": l.execute_index,
                "beginTime": l.begin_time,
                "endTime": l.end_time,
                "duration": l.duration,
                "status": l.status,
                "result": l.result,
                "createTime": l.create_time,
            }
            for l in logs
        ],
        total=total,
        page_no=page_no,
        page_size=page_size,
    )