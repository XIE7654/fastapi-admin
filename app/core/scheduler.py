"""
定时任务服务
基于APScheduler实现
"""
from typing import Callable, Optional, List
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

from app.config import settings
from app.core.redis import redis_client


# 全局调度器
scheduler: Optional[AsyncIOScheduler] = None


def init_scheduler():
    """初始化定时任务调度器"""
    global scheduler

    # 配置JobStore（使用Redis持久化）
    jobstores = {
        "default": RedisJobStore(
            jobs_key="apscheduler.jobs",
            run_times_key="apscheduler.run_times",
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
        )
    }

    # 配置执行器
    executors = {
        "default": ThreadPoolExecutor(20),
    }

    # 创建调度器
    scheduler = AsyncIOScheduler(
        jobstores=jobstores,
        executors=executors,
        timezone="Asia/Shanghai",
    )

    return scheduler


def start_scheduler():
    """启动调度器"""
    global scheduler
    if scheduler:
        scheduler.start()


def shutdown_scheduler():
    """关闭调度器"""
    global scheduler
    if scheduler:
        scheduler.shutdown(wait=False)


def add_cron_job(
    func: Callable,
    job_id: str,
    cron_expr: str = None,
    **cron_kwargs,
):
    """
    添加Cron定时任务

    Args:
        func: 任务函数
        job_id: 任务ID
        cron_expr: Cron表达式（如 "0 9 * * *" 表示每天9点）
        **cron_kwargs: Cron参数（minute, hour, day, month, day_of_week）

    Usage:
        add_cron_job(my_task, "daily_task", hour=9, minute=0)
        add_cron_job(my_task, "daily_task", cron_expr="0 9 * * *")
    """
    global scheduler

    if cron_expr:
        trigger = CronTrigger.from_crontab(cron_expr)
    else:
        trigger = CronTrigger(**cron_kwargs)

    scheduler.add_job(
        func,
        trigger=trigger,
        id=job_id,
        replace_existing=True,
    )


def add_interval_job(
    func: Callable,
    job_id: str,
    seconds: int = None,
    minutes: int = None,
    hours: int = None,
):
    """
    添加间隔任务

    Args:
        func: 任务函数
        job_id: 任务ID
        seconds: 间隔秒数
        minutes: 间隔分钟数
        hours: 间隔小时数

    Usage:
        add_interval_job(my_task, "every_5_min", minutes=5)
    """
    global scheduler

    trigger = IntervalTrigger(
        seconds=seconds,
        minutes=minutes,
        hours=hours,
    )

    scheduler.add_job(
        func,
        trigger=trigger,
        id=job_id,
        replace_existing=True,
    )


def add_one_time_job(
    func: Callable,
    job_id: str,
    run_date: datetime,
):
    """
    添加一次性任务

    Args:
        func: 任务函数
        job_id: 任务ID
        run_date: 执行时间
    """
    global scheduler

    scheduler.add_job(
        func,
        trigger=DateTrigger(run_date),
        id=job_id,
        replace_existing=True,
    )


def remove_job(job_id: str):
    """移除任务"""
    global scheduler
    if scheduler:
        scheduler.remove_job(job_id)


def pause_job(job_id: str):
    """暂停任务"""
    global scheduler
    if scheduler:
        scheduler.pause_job(job_id)


def resume_job(job_id: str):
    """恢复任务"""
    global scheduler
    if scheduler:
        scheduler.resume_job(job_id)


def get_jobs() -> List[dict]:
    """获取所有任务列表"""
    global scheduler
    if not scheduler:
        return []

    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "func": str(job.func),
            "trigger": str(job.trigger),
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
        })

    return jobs


# 定时任务装饰器
def scheduled(
    job_id: str = None,
    cron: str = None,
    interval_seconds: int = None,
    interval_minutes: int = None,
    interval_hours: int = None,
):
    """
    定时任务装饰器

    Usage:
        @scheduled(cron="0 9 * * *")
        async def daily_report():
            ...

        @scheduled(interval_minutes=5)
        async def check_status():
            ...
    """
    def decorator(func: Callable):
        # 保存任务信息，在应用启动时注册
        func._scheduled = {
            "job_id": job_id or func.__name__,
            "cron": cron,
            "interval_seconds": interval_seconds,
            "interval_minutes": interval_minutes,
            "interval_hours": interval_hours,
        }
        return func

    return decorator