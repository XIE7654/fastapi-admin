"""
模型基类
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, DateTime, BigInteger, event
from sqlalchemy.orm import declared_attr, Session

from app.core.database import Base as _Base
from app.core.tenant import get_tenant_id, TenantManager


class Base(_Base):
    """模型基类"""

    __abstract__ = True

    # 主键
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")

    @declared_attr
    def __tablename__(cls):
        """自动生成表名"""
        import re
        name = re.sub(r'([A-Z])', r'_\1', cls.__name__).lower()
        return name.lstrip('_')


class TimestampMixin:
    """时间戳混入类"""

    @declared_attr
    def create_time(cls):
        return Column(DateTime, default=datetime.now, comment="创建时间")

    @declared_attr
    def update_time(cls):
        return Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    @declared_attr
    def creator(cls):
        return Column(BigInteger, nullable=True, comment="创建者")

    @declared_attr
    def updater(cls):
        return Column(BigInteger, nullable=True, comment="更新者")


class TenantMixin:
    """多租户混入类"""

    @declared_attr
    def tenant_id(cls):
        return Column(BigInteger, default=1, index=True, comment="租户编号")

    @declared_attr
    def deleted(cls):
        return Column(Integer, default=0, comment="是否删除: 0-未删除, 1-已删除")


class SoftDeleteMixin:
    """软删除混入类"""

    @declared_attr
    def deleted(cls):
        return Column(Integer, default=0, comment="是否删除: 0-未删除, 1-已删除")


def _get_current_user_id() -> Optional[int]:
    """获取当前用户ID"""
    try:
        from app.core.user_context import get_user_id
        return get_user_id()
    except Exception:
        return None


def _get_current_tenant_id() -> int:
    """获取当前租户ID"""
    return TenantManager.get_tenant_id_or_default()


@event.listens_for(Session, 'before_flush')
def _before_flush(session, context, instances):
    """
    在 flush 前自动设置公共字段
    使用 Session 级别的事件，确保所有模型都能触发
    """
    from datetime import datetime

    # 获取当前用户ID
    user_id = _get_current_user_id()
    now = datetime.now()

    # 处理新增的对象
    for instance in session.new:
        # 设置创建时间和创建者
        if hasattr(instance, 'create_time') and instance.create_time is None:
            instance.create_time = now
        if hasattr(instance, 'update_time') and instance.update_time is None:
            instance.update_time = now
        if hasattr(instance, 'creator') and instance.creator is None and user_id is not None:
            instance.creator = user_id
        if hasattr(instance, 'updater') and instance.updater is None and user_id is not None:
            instance.updater = user_id

        # 设置租户ID（如果模型有 tenant_id 字段且不是忽略的表）
        if hasattr(instance, 'tenant_id') and instance.tenant_id is None:
            table_name = instance.__tablename__
            if not TenantManager.is_ignore_table(table_name):
                instance.tenant_id = _get_current_tenant_id()

        # 设置 deleted 默认值
        if hasattr(instance, 'deleted') and instance.deleted is None:
            instance.deleted = 0

    # 处理修改的对象
    for instance in session.dirty:
        # 设置更新时间和更新者
        if hasattr(instance, 'update_time'):
            instance.update_time = now
        if hasattr(instance, 'updater') and user_id is not None:
            instance.updater = user_id