"""
用户上下文管理
使用 contextvars 实现请求级别的用户上下文
"""
from typing import Optional
from contextvars import ContextVar
from dataclasses import dataclass


@dataclass
class UserContext:
    """用户上下文信息"""
    id: int
    username: Optional[str] = None
    nickname: Optional[str] = None


# 用户上下文变量
_user_context: ContextVar[Optional[UserContext]] = ContextVar(
    "user_context",
    default=None
)


def set_user(user_id: int, username: str = None, nickname: str = None):
    """
    设置当前用户上下文

    Args:
        user_id: 用户ID
        username: 用户名
        nickname: 昵称
    """
    context = UserContext(
        id=user_id,
        username=username,
        nickname=nickname
    )
    _user_context.set(context)


def get_user() -> Optional[UserContext]:
    """
    获取当前用户上下文

    Returns:
        当前用户上下文，未设置返回None
    """
    return _user_context.get()


def get_user_id() -> Optional[int]:
    """
    获取当前用户ID

    Returns:
        当前用户ID，未设置返回None
    """
    context = get_user()
    return context.id if context else None


def clear_user():
    """清除用户上下文"""
    _user_context.set(None)