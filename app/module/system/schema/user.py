"""
用户相关Schema
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator

from app.common.pagination import PageQuery


class UserBase(BaseModel):
    """用户基础信息"""

    username: Optional[str] = Field(None, max_length=30, description="用户账号")
    nickname: Optional[str] = Field(None, max_length=30, description="用户昵称")
    email: Optional[str] = Field(None, max_length=50, description="邮箱")
    mobile: Optional[str] = Field(None, max_length=20, description="手机号码")
    gender: Optional[int] = Field(default=0, ge=0, le=2, description="性别: 0-未知, 1-男, 2-女")
    dept_id: Optional[int] = Field(None, description="部门ID")
    post_ids: Optional[List[int]] = Field(None, description="岗位ID列表")
    status: Optional[int] = Field(default=0, ge=0, le=1, description="状态: 0-正常, 1-禁用")
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class UserCreate(UserBase):
    """创建用户请求"""

    username: str = Field(..., max_length=30, description="用户账号")
    nickname: str = Field(..., max_length=30, description="用户昵称")
    password: str = Field(..., min_length=6, max_length=20, description="密码")
    dept_id: int = Field(..., description="部门ID")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("用户账号不能为空")
        return v.strip()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("密码长度不能少于6位")
        return v


class UserUpdate(BaseModel):
    """更新用户请求"""

    id: int = Field(..., description="用户ID")
    nickname: Optional[str] = Field(None, max_length=30, description="用户昵称")
    email: Optional[str] = Field(None, max_length=50, description="邮箱")
    mobile: Optional[str] = Field(None, max_length=20, description="手机号码")
    gender: Optional[int] = Field(None, ge=0, le=2, description="性别")
    dept_id: Optional[int] = Field(None, description="部门ID")
    post_ids: Optional[List[int]] = Field(None, description="岗位ID列表")
    status: Optional[int] = Field(None, ge=0, le=1, description="状态")
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class UserResponse(UserBase):
    """用户响应"""

    id: int = Field(..., description="用户ID")
    avatar: Optional[str] = Field(None, description="头像")
    login_ip: Optional[str] = Field(None, description="最后登录IP")
    login_date: Optional[datetime] = Field(None, description="最后登录时间")
    create_time: Optional[datetime] = Field(None, description="创建时间")

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def convert_fields(cls, data):
        """转换数据库字段到schema字段"""
        # 处理 post_ids: 字符串 -> 列表
        if hasattr(data, "post_ids") and isinstance(data.post_ids, str):
            if data.post_ids:
                data.post_ids = [int(pid) for pid in data.post_ids.split(",") if pid]
            else:
                data.post_ids = []
        # 处理 gender/sex 字段映射
        if hasattr(data, "sex") and not hasattr(data, "gender"):
            data.gender = data.sex
        return data


class UserSimpleResponse(BaseModel):
    """用户简要响应"""

    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户账号")
    nickname: str = Field(..., description="用户昵称")
    dept_id: Optional[int] = Field(None, description="部门ID")

    model_config = {"from_attributes": True}


class UserPageQuery(PageQuery):
    """用户分页查询"""

    username: Optional[str] = Field(None, description="用户账号")
    nickname: Optional[str] = Field(None, description="用户昵称")
    mobile: Optional[str] = Field(None, description="手机号码")
    status: Optional[int] = Field(None, ge=0, le=1, description="状态")
    dept_id: Optional[int] = Field(None, description="部门ID")
    create_time: Optional[List[datetime]] = Field(None, description="创建时间范围")


class UserPasswordUpdate(BaseModel):
    """修改密码请求"""

    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=20, description="新密码")


class UserResetPassword(BaseModel):
    """重置密码请求"""

    id: int = Field(..., description="用户ID")
    password: str = Field(..., min_length=6, max_length=20, description="新密码")