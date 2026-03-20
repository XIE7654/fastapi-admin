"""
菜单模型
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, BigInteger, SmallInteger, Text

from app.module.system.model.base import Base, TimestampMixin


class Menu(Base, TimestampMixin):
    """菜单表"""

    __tablename__ = "system_menu"

    name = Column(String(50), nullable=False, comment="菜单名称")
    permission = Column(String(100), nullable=True, comment="权限标识")
    type = Column(SmallInteger, nullable=False, comment="菜单类型: 1-目录, 2-菜单, 3-按钮")
    sort = Column(Integer, default=0, comment="显示顺序")
    parent_id = Column(BigInteger, default=0, comment="父菜单ID")
    path = Column(String(200), nullable=True, comment="路由地址")
    icon = Column(String(100), nullable=True, comment="菜单图标")
    component = Column(String(255), nullable=True, comment="组件路径")
    component_name = Column(String(100), nullable=True, comment="组件名称")
    status = Column(SmallInteger, default=0, comment="状态: 0-正常, 1-禁用")
    visible = Column(SmallInteger, default=0, comment="是否可见: 0-是, 1-否")
    keep_alive = Column(SmallInteger, default=0, comment="是否缓存: 0-否, 1-是")
    always_show = Column(SmallInteger, default=0, comment="是否总是显示: 0-否, 1-是")

    def __repr__(self):
        return f"<Menu(id={self.id}, name={self.name}, type={self.type})>"

    @property
    def is_directory(self) -> bool:
        """是否是目录"""
        return self.type == 1

    @property
    def is_menu(self) -> bool:
        """是否是菜单"""
        return self.type == 2

    @property
    def is_button(self) -> bool:
        """是否是按钮"""
        return self.type == 3

    @property
    def is_active(self) -> bool:
        """是否激活"""
        return self.status == 0