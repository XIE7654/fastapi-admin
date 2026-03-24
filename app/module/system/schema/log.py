"""
日志相关Schema
"""
from typing import Optional, List
from datetime import datetime
from pydantic import Field

from app.common.schema import CamelModel, CamelORMModel
from app.common.pagination import PageQuery


# ==================== 操作日志 ====================

class OperateLogResponse(CamelORMModel):
    """操作日志响应"""

    id: int = Field(..., description="日志ID")
    trace_id: Optional[str] = Field(None, description="链路追踪编号")
    user_id: Optional[int] = Field(None, description="用户ID")
    user_type: Optional[int] = Field(None, description="用户类型")
    type: Optional[str] = Field(None, description="操作模块类型")
    sub_type: Optional[str] = Field(None, description="操作名")
    biz_id: Optional[int] = Field(None, description="操作数据模块编号")
    action: Optional[str] = Field(None, description="操作内容")
    extra: Optional[str] = Field(None, description="拓展字段")
    request_method: Optional[str] = Field(None, description="请求方法")
    request_url: Optional[str] = Field(None, description="请求地址")
    user_ip: Optional[str] = Field(None, description="用户IP")
    user_agent: Optional[str] = Field(None, description="浏览器UA")
    create_time: Optional[datetime] = Field(None, description="创建时间")


class OperateLogPageQuery(PageQuery):
    """操作日志分页查询"""

    user_id: Optional[int] = Field(None, description="用户ID")
    type: Optional[str] = Field(None, description="操作模块类型")
    sub_type: Optional[str] = Field(None, description="操作名")
    create_time: Optional[List[datetime]] = Field(None, description="创建时间范围")


# ==================== 登录日志 ====================

class LoginLogResponse(CamelORMModel):
    """登录日志响应"""

    id: int = Field(..., description="日志ID")
    log_type: Optional[int] = Field(None, description="日志类型")
    trace_id: Optional[str] = Field(None, description="链路追踪编号")
    user_id: Optional[int] = Field(None, description="用户ID")
    username: Optional[str] = Field(None, description="用户账号")
    user_type: Optional[int] = Field(None, description="用户类型")
    result: Optional[int] = Field(None, description="结果码")
    user_ip: Optional[str] = Field(None, description="用户IP")
    user_agent: Optional[str] = Field(None, description="浏览器UA")
    create_time: Optional[datetime] = Field(None, description="登录时间")


class LoginLogPageQuery(PageQuery):
    """登录日志分页查询"""

    user_id: Optional[int] = Field(None, description="用户ID")
    username: Optional[str] = Field(None, description="用户账号")
    log_type: Optional[int] = Field(None, description="日志类型")
    result: Optional[int] = Field(None, description="结果码")
    user_ip: Optional[str] = Field(None, description="用户IP")
    create_time: Optional[List[datetime]] = Field(None, description="登录时间范围")