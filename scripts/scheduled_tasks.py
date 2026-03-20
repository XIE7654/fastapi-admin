"""
定时任务示例
演示如何使用定时任务装饰器
"""
import asyncio
from datetime import datetime

from app.core.scheduler import scheduled, add_cron_job, add_interval_job
from app.core.metrics import set_online_users
from app.module.system.service.online_user import OnlineUserService
from loguru import logger


# ==================== 使用装饰器定义定时任务 ====================

@scheduled(cron="0 0 * * *")  # 每天凌晨执行
async def daily_cleanup_task():
    """每日清理任务"""
    logger.info(f"开始执行每日清理任务: {datetime.now()}")
    # TODO: 清理过期数据、临时文件等
    logger.info("每日清理任务完成")


@scheduled(interval_hours=1)  # 每小时执行
async def hourly_stats_task():
    """每小时统计任务"""
    logger.info(f"开始执行小时统计任务: {datetime.now()}")
    # TODO: 统计数据、生成报表等
    logger.info("小时统计任务完成")


@scheduled(interval_minutes=5)  # 每5分钟执行
async def update_online_users_count():
    """更新在线用户数"""
    try:
        users = await OnlineUserService.get_online_users()
        count = len(users)
        set_online_users(count)
        logger.info(f"当前在线用户数: {count}")
    except Exception as e:
        logger.error(f"更新在线用户数失败: {e}")


# ==================== 手动注册定时任务 ====================

def register_scheduled_tasks():
    """注册所有定时任务"""

    # 注册Cron任务
    add_cron_job(
        daily_cleanup_task,
        job_id="daily_cleanup",
        cron_expr="0 0 * * *"
    )

    # 注册间隔任务
    add_interval_job(
        hourly_stats_task,
        job_id="hourly_stats",
        hours=1
    )

    add_interval_job(
        update_online_users_count,
        job_id="update_online_users",
        minutes=5
    )

    logger.info("定时任务注册完成")


# ==================== 任务管理API示例 ====================

async def get_task_status(job_id: str) -> dict:
    """获取任务状态"""
    from app.core.scheduler import get_jobs

    jobs = get_jobs()
    for job in jobs:
        if job["id"] == job_id:
            return job
    return None


async def run_task_manually(job_id: str):
    """手动触发任务"""
    tasks = {
        "daily_cleanup": daily_cleanup_task,
        "hourly_stats": hourly_stats_task,
        "update_online_users": update_online_users_count,
    }

    task = tasks.get(job_id)
    if task:
        await task()
        return True
    return False


if __name__ == "__main__":
    # 测试定时任务
    asyncio.run(update_online_users_count())