"""
部门模型
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, BigInteger, SmallInteger, Text

from app.module.system.model.base import Base, TimestampMixin, TenantMixin


class Dept(Base, TimestampMixin, TenantMixin):
    """部门表"""

    __tablename__ = "system_dept"

    name = Column(String(50), nullable=False, comment="部门名称")
    parent_id = Column(BigInteger, default=0, comment="父部门ID")
    sort = Column(Integer, default=0, comment="显示顺序")
    leader_user_id = Column(BigInteger, nullable=True, comment="负责人用户ID")
    phone = Column(String(20), nullable=True, comment="联系电话")
    email = Column(String(50), nullable=True, comment="邮箱")
    status = Column(SmallInteger, default=0, comment="状态: 0-正常, 1-禁用")

    def __repr__(self):
        return f"<Dept(id={self.id}, name={self.name})>"

    @property
    def is_active(self) -> bool:
        """是否激活"""
        return self.status == 0

    @property
    def is_root(self) -> bool:
        """是否是根部门"""
        return self.parent_id == 0


class DeptTree:
    """部门树结构"""

    def __init__(self, dept: Dept):
        self.id = dept.id
        self.name = dept.name
        self.parent_id = dept.parent_id
        self.sort = dept.sort
        self.status = dept.status
        self.children: List['DeptTree'] = []

    def add_child(self, child: 'DeptTree'):
        """添加子部门"""
        self.children.append(child)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "parentId": self.parent_id,
            "sort": self.sort,
            "status": self.status,
            "children": [child.to_dict() for child in self.children]
        }