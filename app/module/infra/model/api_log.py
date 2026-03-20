"""
API 访问日志模型
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, BigInteger, SmallInteger, Text, Index

from app.module.infra.model.base import Base, TimestampMixin, TenantMixin


class ApiAccessLog(Base, TimestampMixin, TenantMixin):
    """API 访问日志表"""

    __tablename__ = "infra_api_access_log"

    trace_id = Column(String(64), nullable=False, default="", comment="链路追踪编号")
    user_id = Column(BigInteger, nullable=False, default=0, comment="用户编号")
    user_type = Column(SmallInteger, nullable=False, default=0, comment="用户类型")
    application_name = Column(String(50), nullable=False, comment="应用名")
    request_method = Column(String(16), nullable=False, default="", comment="请求方法名")
    request_url = Column(String(255), nullable=False, default="", comment="请求地址")
    request_params = Column(Text, nullable=True, comment="请求参数")
    response_body = Column(Text, nullable=True, comment="响应结果")
    user_ip = Column(String(50), nullable=False, comment="用户IP")
    user_agent = Column(String(512), nullable=False, comment="浏览器UA")
    operate_module = Column(String(50), nullable=True, comment="操作模块")
    operate_name = Column(String(50), nullable=True, comment="操作名")
    operate_type = Column(SmallInteger, nullable=True, default=0, comment="操作分类")
    begin_time = Column(DateTime, nullable=False, comment="开始请求时间")
    end_time = Column(DateTime, nullable=False, comment="结束请求时间")
    duration = Column(Integer, nullable=False, comment="执行时长")
    result_code = Column(Integer, nullable=False, default=0, comment="结果码")
    result_msg = Column(String(512), nullable=True, default="", comment="结果提示")

    __table_args__ = (
        Index('idx_create_time', 'create_time'),
    )


class ApiErrorLog(Base, TimestampMixin, TenantMixin):
    """API 异常日志表"""

    __tablename__ = "infra_api_error_log"

    trace_id = Column(String(64), nullable=False, comment="链路追踪编号")
    user_id = Column(BigInteger, nullable=False, default=0, comment="用户编号")
    user_type = Column(SmallInteger, nullable=False, default=0, comment="用户类型")
    application_name = Column(String(50), nullable=False, comment="应用名")
    request_method = Column(String(16), nullable=False, comment="请求方法名")
    request_url = Column(String(255), nullable=False, comment="请求地址")
    request_params = Column(String(8000), nullable=False, comment="请求参数")
    user_ip = Column(String(50), nullable=False, comment="用户IP")
    user_agent = Column(String(512), nullable=False, comment="浏览器UA")
    exception_time = Column(DateTime, nullable=False, comment="异常发生时间")
    exception_name = Column(String(128), nullable=False, default="", comment="异常名")
    exception_message = Column(Text, nullable=False, comment="异常导致的消息")
    exception_root_cause_message = Column(Text, nullable=False, comment="异常导致的根消息")
    exception_stack_trace = Column(Text, nullable=False, comment="异常的栈轨迹")
    exception_class_name = Column(String(512), nullable=False, comment="异常发生的类全名")
    exception_file_name = Column(String(512), nullable=False, comment="异常发生的类文件")
    exception_method_name = Column(String(512), nullable=False, comment="异常发生的方法名")
    exception_line_number = Column(Integer, nullable=False, comment="异常发生的方法所在行")
    process_status = Column(SmallInteger, nullable=False, comment="处理状态")
    process_time = Column(DateTime, nullable=True, comment="处理时间")
    process_user_id = Column(Integer, nullable=True, default=0, comment="处理用户编号")