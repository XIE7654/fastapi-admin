"""
角色模型
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, BigInteger, SmallInteger, Text

from app.module.system.model.base import Base, TimestampMixin, TenantMixin


class Role(Base, TimestampMixin, TenantMixin):
    """角色表"""

    __tablename__ = "system_role"

    name = Column(String(30), nullable=False, comment="角色名称")
    code = Column(String(100), unique=True, nullable=False, comment="角色编码")
    sort = Column(Integer, default=0, comment="显示顺序")
    data_scope = Column(SmallInteger, default=1, comment="数据范围: 1-全部, 2-自定义, 3-本部门, 4-本部门及以下, 5-仅本人")
    data_scope_dept_ids = Column(String(500), nullable=True, comment="数据范围部门ID列表")
    status = Column(SmallInteger, default=0, comment="状态: 0-正常, 1-禁用")
    remark = Column(String(500), nullable=True, comment="备注")
    type = Column(SmallInteger, default=2, comment="角色类型: 1-系统内置, 2-自定义")

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name}, code={self.code})>"

    @property
    def is_active(self) -> bool:
        """是否激活"""
        return self.status == 0

    @property
    def is_system(self) -> bool:
        """是否系统内置"""
        return self.type == 1

    def get_data_scope_dept_ids_list(self) -> List[int]:
        """获取数据范围部门ID列表"""
        if not self.data_scope_dept_ids:
            return []
        return [int(did) for did in self.data_scope_dept_ids.split(",") if did]


class RoleMenu(Base):
    """角色-菜单关联表"""

    __tablename__ = "system_role_menu"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    role_id = Column(BigInteger, nullable=False, comment="角色ID")
    menu_id = Column(BigInteger, nullable=False, comment="菜单ID")