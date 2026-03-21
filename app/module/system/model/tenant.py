"""
租户模型
"""
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, BigInteger, SmallInteger

from app.module.system.model.base import Base, TimestampMixin


class Tenant(Base, TimestampMixin):
    """租户表"""

    __tablename__ = "system_tenant"

    name = Column(String(30), nullable=False, comment="租户名称")
    contact_user_id = Column(BigInteger, nullable=True, comment="联系人的用户编号")
    contact_name = Column(String(30), nullable=True, comment="联系人")
    contact_mobile = Column(String(500), nullable=True, comment="联系手机")
    status = Column(SmallInteger, default=0, comment="租户状态: 0-正常, 1-禁用")
    websites = Column(String(1024), nullable=True, comment="绑定域名数组")
    package_id = Column(BigInteger, nullable=True, comment="租户套餐编号")
    expire_time = Column(DateTime, nullable=True, comment="过期时间")
    account_count = Column(Integer, default=0, comment="用户数量")

    def __repr__(self):
        return f"<Tenant(id={self.id}, name={self.name})>"

    @property
    def is_active(self) -> bool:
        """是否激活"""
        return self.status == 0

    @property
    def is_expired(self) -> bool:
        """是否已过期"""
        if not self.expire_time:
            return False
        return datetime.now() > self.expire_time


class TenantPackage(Base, TimestampMixin):
    """租户套餐表"""

    __tablename__ = "system_tenant_package"

    name = Column(String(30), nullable=False, comment="套餐名称")
    status = Column(SmallInteger, default=0, comment="租户状态: 0-正常, 1-禁用")
    remark = Column(String(256), nullable=True, comment="备注")
    menu_ids = Column(String(4096), nullable=True, comment="关联的菜单编号列表")