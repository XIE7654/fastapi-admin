"""
日志相关Schema
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from app.common.pagination import PageQuery


# ==================== 操作日志 ====================

class OperateLogResponse(BaseModel):
    """操作日志响应"""

    id: int = Field(..., description="日志ID")
    module: Optional[str] = Field(None, description="模块标题")
    name: Optional[str] = Field(None, description="操作名")
    type: Optional[int] = Field(None, description="操作分类")
    request_method: Optional[str] = Field(None, description="请求方法")
    request_url: Optional[str] = Field(None, description="请求地址")
    request_params: Optional[str] = Field(None, description="请求参数")
    user_agent: Optional[str] = Field(None, description="浏览器")
    duration: Optional[int] = Field(None, description="执行时长(ms)")
    result_code: Optional[int] = Field(None, description="结果码")
    result_msg: Optional[str] = Field(None, description="结果提示")
    user_id: Optional[int] = Field(None, description="用户ID")
    user_name: Optional[str] = Field(None, description="用户昵称")
    user_ip: Optional[str] = Field(None, description="用户IP")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    create_time: Optional[datetime] = Field(None, description="创建时间")

    model_config = {"from_attributes": True}


class OperateLogPageQuery(PageQuery):
    """操作日志分页查询"""

    module: Optional[str] = Field(None, description="模块标题")
    user_id: Optional[int] = Field(None, description="用户ID")
    user_name: Optional[str] = Field(None, description="用户昵称")
    type: Optional[int] = Field(None, description="操作分类")
    result_code: Optional[int] = Field(None, description="结果码")
    start_time: Optional[List[datetime]] = Field(None, description="开始时间范围")


# ==================== 登录日志 ====================

class LoginLogResponse(BaseModel):
    """登录日志响应"""

    id: int = Field(..., description="日志ID")
    log_type: Optional[int] = Field(None, description="日志类型")
    trace_id: Optional[str] = Field(None, description="链路追踪编号")
    user_id: Optional[int] = Field(None, description="用户ID")
    username: Optional[str] = Field(None, description="用户账号")
    user_type: Optional[int] = Field(None, description="用户类型")
    result_code: Optional[int] = Field(None, description="结果码")
    result_msg: Optional[str] = Field(None, description="结果提示")
    user_ip: Optional[str] = Field(None, description="用户IP")
    user_ip_area: Optional[str] = Field(None, description="用户IP地区")
    browser: Optional[str] = Field(None, description="浏览器名")
    os: Optional[str] = Field(None, description="操作系统")
    login_time: Optional[datetime] = Field(None, description="登录时间")

    model_config = {"from_attributes": True}


class LoginLogPageQuery(PageQuery):
    """登录日志分页查询"""

    user_id: Optional[int] = Field(None, description="用户ID")
    username: Optional[str] = Field(None, description="用户账号")
    log_type: Optional[int] = Field(None, description="日志类型")
    result_code: Optional[int] = Field(None, description="结果码")
    user_ip: Optional[str] = Field(None, description="用户IP")
    login_time: Optional[List[datetime]] = Field(None, description="登录时间范围")