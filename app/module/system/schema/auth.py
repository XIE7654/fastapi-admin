"""
认证相关Schema
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """登录请求"""

    username: str = Field(..., description="用户账号")
    password: str = Field(..., description="密码")
    captcha: Optional[str] = Field(None, description="验证码")
    uuid: Optional[str] = Field(None, description="验证码唯一标识")
    tenant_id: Optional[int] = Field(None, description="租户ID")

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "admin",
                "password": "123456",
                "captcha": "1234",
                "uuid": "xxx-xxx-xxx"
            }
        }
    }


class SmsLoginRequest(BaseModel):
    """短信登录请求"""

    mobile: str = Field(..., description="手机号码")
    code: str = Field(..., description="短信验证码")


class TokenResponse(BaseModel):
    """Token响应"""

    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="Bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间(秒)")


class LoginResponse(BaseModel):
    """登录响应"""

    user_id: int = Field(..., alias="userId", description="用户ID")
    access_token: str = Field(..., alias="accessToken", description="访问令牌")
    refresh_token: str = Field(..., alias="refreshToken", description="刷新令牌")
    expires_time: int = Field(..., alias="expiresTime", description="过期时间戳(毫秒)")

    model_config = {"populate_by_name": True}


class RefreshTokenRequest(BaseModel):
    """刷新Token请求"""

    refresh_token: str = Field(..., description="刷新令牌")


class LogoutRequest(BaseModel):
    """登出请求"""

    token: Optional[str] = Field(None, description="访问令牌")


class CaptchaResponse(BaseModel):
    """验证码响应"""

    uuid: str = Field(..., description="验证码唯一标识")
    img: str = Field(..., description="验证码图片Base64")


class PermissionInfoResponse(BaseModel):
    """用户权限信息响应"""

    user: dict = Field(..., description="用户信息")
    roles: List[str] = Field(default_factory=list, description="角色列表")
    permissions: List[str] = Field(default_factory=list, description="权限列表")
    menus: List[dict] = Field(default_factory=list, description="菜单列表")


class MenuVO(BaseModel):
    """菜单VO"""

    id: int = Field(..., description="菜单ID")
    name: str = Field(..., description="菜单名称")
    parent_id: int = Field(default=0, description="父菜单ID")
    sort: int = Field(default=0, description="排序")
    path: Optional[str] = Field(None, description="路由路径")
    icon: Optional[str] = Field(None, description="图标")
    component: Optional[str] = Field(None, description="组件路径")
    component_name: Optional[str] = Field(None, description="组件名称")
    visible: int = Field(default=0, description="是否可见")
    keep_alive: int = Field(default=0, description="是否缓存")
    type: int = Field(..., description="类型: 1-目录, 2-菜单, 3-按钮")
    permission: Optional[str] = Field(None, description="权限标识")
    children: List['MenuVO'] = Field(default_factory=list, description="子菜单")

    model_config = {"from_attributes": True}