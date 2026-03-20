"""
控制器模块
"""
from app.module.system.controller import auth, user, role, menu, dept, dict, post
from app.module.system.controller import log, config, online_user, tenant

__all__ = [
    "auth",
    "user",
    "role",
    "menu",
    "dept",
    "dict",
    "post",
    "log",
    "config",
    "online_user",
    "tenant",
]