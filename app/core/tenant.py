"""
多租户上下文管理
使用 contextvars 实现请求级别的租户隔离
"""
from typing import Optional
from contextvars import ContextVar
from dataclasses import dataclass


@dataclass
class TenantContext:
    """租户上下文信息"""
    id: int
    name: Optional[str] = None
    code: Optional[str] = None


# 租户上下文变量
_tenant_context: ContextVar[Optional[TenantContext]] = ContextVar(
    "tenant_context",
    default=None
)


def set_tenant(tenant_id: int, tenant_name: str = None, tenant_code: str = None):
    """
    设置当前租户上下文

    Args:
        tenant_id: 租户ID
        tenant_name: 租户名称
        tenant_code: 租户编码
    """
    context = TenantContext(
        id=tenant_id,
        name=tenant_name,
        code=tenant_code
    )
    _tenant_context.set(context)


def get_tenant() -> Optional[TenantContext]:
    """
    获取当前租户上下文

    Returns:
        当前租户上下文，未设置返回None
    """
    return _tenant_context.get()


def get_tenant_id() -> Optional[int]:
    """
    获取当前租户ID

    Returns:
        当前租户ID，未设置返回None
    """
    context = get_tenant()
    return context.id if context else None


def clear_tenant():
    """清除租户上下文"""
    _tenant_context.set(None)


class TenantManager:
    """租户管理器"""

    # 默认租户ID（用于非租户场景）
    DEFAULT_TENANT_ID = 1

    # 忽略租户过滤的表
    IGNORE_TABLES = [
        "system_tenant",
        "system_tenant_package",
        "system_user",
        "system_role",
        "system_menu",
        "system_dict_type",
        "system_dict_data",
        "system_dept",
        "system_post",
        "system_oauth2_client",
        "infra_file",
        "infra_file_config",
    ]

    # 租户ID字段名
    TENANT_ID_COLUMN = "tenant_id"

    @classmethod
    def is_ignore_table(cls, table_name: str) -> bool:
        """检查是否是忽略租户过滤的表"""
        return table_name in cls.IGNORE_TABLES

    @classmethod
    def get_tenant_id_or_default(cls) -> int:
        """获取租户ID，未设置则返回默认值"""
        tenant_id = get_tenant_id()
        return tenant_id if tenant_id is not None else cls.DEFAULT_TENANT_ID