"""
系统模块
"""
# 导入控制器路由
from app.module.system.controller import auth, user, role, menu, dept, dict, post

__all__ = [
    "auth",
    "user",
    "role",
    "menu",
    "dept",
    "dict",
    "post",
]