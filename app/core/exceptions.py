"""
全局异常定义
"""
from typing import Optional, Any


class BusinessException(Exception):
    """业务异常基类"""

    def __init__(
        self,
        code: int = 500,
        message: str = "系统错误",
        data: Optional[Any] = None
    ):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(self.message)


class UnauthorizedException(BusinessException):
    """未授权异常"""

    def __init__(self, message: str = "未授权，请登录"):
        super().__init__(code=401, message=message)


class ForbiddenException(BusinessException):
    """禁止访问异常"""

    def __init__(self, message: str = "无权限访问"):
        super().__init__(code=403, message=message)


class NotFoundException(BusinessException):
    """资源未找到异常"""

    def __init__(self, message: str = "资源不存在"):
        super().__init__(code=404, message=message)


class ValidationException(BusinessException):
    """参数验证异常"""

    def __init__(self, message: str = "参数错误"):
        super().__init__(code=400, message=message)


class TenantException(BusinessException):
    """租户异常"""

    def __init__(self, message: str = "租户信息错误"):
        super().__init__(code=1001, message=message)


class AuthenticationException(BusinessException):
    """认证异常"""

    def __init__(self, message: str = "认证失败"):
        super().__init__(code=1002, message=message)


# 错误码常量
class ErrorCode:
    """错误码定义"""

    # 系统级错误 1000-1999
    SUCCESS = 0
    SYSTEM_ERROR = 500
    PARAM_ERROR = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404

    # 认证错误 2000-2999
    USER_NOT_EXISTS = 2001
    USER_PASSWORD_INCORRECT = 2002
    USER_DISABLED = 2003
    USER_EXPIRED = 2004
    TOKEN_EXPIRED = 2005
    TOKEN_INVALID = 2006
    CAPTCHA_ERROR = 2007
    CAPTCHA_EXPIRED = 2008

    # 租户错误 3000-3999
    TENANT_NOT_EXISTS = 3001
    TENANT_DISABLED = 3002
    TENANT_EXPIRED = 3003

    # 权限错误 4000-4999
    PERMISSION_DENIED = 4001
    ROLE_NOT_EXISTS = 4002
    MENU_NOT_EXISTS = 4003

    # 数据错误 5000-5999
    DATA_EXISTS = 5001
    DATA_NOT_EXISTS = 5002
    DATA_STATUS_ERROR = 5003