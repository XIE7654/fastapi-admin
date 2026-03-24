"""
装饰器
"""
from functools import wraps
from typing import Callable, Optional, Any
import asyncio
import logging

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class OperateLog:
    """
    操作日志装饰器

    使用示例:
        @OperateLog(type="用户管理", sub_type="创建用户", biz_id=lambda r: r.id)
        async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
            ...

        # 或者直接指定业务ID
        @OperateLog(type="用户管理", sub_type="删除用户", biz_id=1)
        async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
            ...

        # 使用 action 函数动态生成操作内容
        @OperateLog(
            type="用户管理",
            sub_type="更新用户",
            biz_id=lambda result: result.get("id"),
            action=lambda result: f"更新用户 {result.get('username')}"
        )
        async def update_user(user_id: int, user: UserUpdate, db: AsyncSession = Depends(get_db)):
            ...
    """

    def __init__(
        self,
        type: str,
        sub_type: str,
        biz_id: Any = 0,
        action: Optional[str] = None,
        extra: Optional[str] = None,
        success: bool = True,
    ):
        """
        初始化操作日志装饰器

        Args:
            type: 操作模块类型，如 "用户管理"
            sub_type: 操作名称，如 "创建用户"
            biz_id: 业务编号，可以是固定值或函数（接收返回值作为参数）
            action: 操作内容描述
            extra: 扩展字段（JSON格式）
            success: 操作是否成功
        """
        self.type = type
        self.sub_type = sub_type
        self.biz_id = biz_id
        self.action = action
        self.extra = extra
        self.success = success

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取请求信息
            request = kwargs.get("request")
            db = kwargs.get("db")

            # 尝试从依赖注入获取用户信息
            current_user = kwargs.get("current_user")

            # 执行原函数
            result = await func(*args, **kwargs)

            # 记录操作日志（异步，不阻塞主流程）
            if db and isinstance(db, AsyncSession):
                try:
                    await self._create_log(
                        db=db,
                        request=request,
                        current_user=current_user,
                        result=result,
                    )
                except Exception as e:
                    logger.error(f"记录操作日志失败: {e}")

            return result

        return wrapper

    async def _create_log(
        self,
        db: AsyncSession,
        request: Optional[Request],
        current_user: Optional[Any],
        result: Any,
    ):
        """创建操作日志"""
        from app.module.system.service.operate_log import OperateLogService

        # 解析业务ID
        biz_id = 0
        if callable(self.biz_id):
            try:
                biz_id = self.biz_id(result)
                if biz_id is None:
                    biz_id = 0
            except Exception:
                biz_id = 0
        elif isinstance(self.biz_id, (int, str)):
            biz_id = int(self.biz_id) if self.biz_id else 0

        # 解析操作内容
        action = self.action
        if callable(action):
            try:
                action = action(result)
            except Exception:
                action = None

        # 获取用户信息
        user_id = 0
        user_type = 2  # 默认普通用户
        tenant_id = 1

        if current_user:
            user_id = getattr(current_user, "id", 0)
            user_type = getattr(current_user, "user_type", 2)
            tenant_id = getattr(current_user, "tenant_id", 1)

        # 获取请求信息
        request_method = None
        request_url = None
        user_ip = None
        user_agent = None

        if request:
            request_method = request.method
            request_url = str(request.url.path)
            user_ip = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")

        # 创建日志
        await OperateLogService.create(
            db=db,
            user_id=user_id,
            user_type=user_type,
            type=self.type,
            sub_type=self.sub_type,
            biz_id=biz_id,
            action=action,
            extra=self.extra,
            request_method=request_method,
            request_url=request_url,
            user_ip=user_ip,
            user_agent=user_agent,
            tenant_id=tenant_id,
            success=self.success,
        )


def operate_log(
    type: str,
    sub_type: str,
    biz_id: Any = 0,
    action: Optional[str] = None,
    extra: Optional[str] = None,
    success: bool = True,
):
    """
    操作日志装饰器（函数式用法）

    使用示例:
        @operate_log(type="用户管理", sub_type="创建用户")
        async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
            ...
    """
    return OperateLog(
        type=type,
        sub_type=sub_type,
        biz_id=biz_id,
        action=action,
        extra=extra,
        success=success,
    )