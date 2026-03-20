"""
定时任务模型
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, BigInteger, SmallInteger, Text

from app.module.infra.model.base import Base, TimestampMixin


class Job(Base, TimestampMixin):
    """定时任务表"""

    __tablename__ = "infra_job"

    name = Column(String(32), nullable=False, comment="任务名称")
    status = Column(SmallInteger, nullable=False, comment="任务状态")
    handler_name = Column(String(64), nullable=False, comment="处理器的名字")
    handler_param = Column(String(255), nullable=True, comment="处理器的参数")
    cron_expression = Column(String(32), nullable=False, comment="CRON表达式")
    retry_count = Column(Integer, nullable=False, default=0, comment="重试次数")
    retry_interval = Column(Integer, nullable=False, default=0, comment="重试间隔")
    monitor_timeout = Column(Integer, nullable=False, default=0, comment="监控超时时间")


class JobLog(Base, TimestampMixin):
    """定时任务日志表"""

    __tablename__ = "infra_job_log"

    job_id = Column(BigInteger, nullable=False, comment="任务编号")
    handler_name = Column(String(64), nullable=False, comment="处理器的名字")
    handler_param = Column(String(255), nullable=True, comment="处理器的参数")
    execute_index = Column(SmallInteger, nullable=False, default=1, comment="第几次执行")
    begin_time = Column(DateTime, nullable=False, comment="开始执行时间")
    end_time = Column(DateTime, nullable=True, comment="结束执行时间")
    duration = Column(Integer, nullable=True, comment="执行时长")
    status = Column(SmallInteger, nullable=False, comment="任务状态")
    result = Column(String(4000), nullable=True, default="", comment="结果数据")