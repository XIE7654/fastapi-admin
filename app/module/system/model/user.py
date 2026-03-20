"""
用户模型
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, BigInteger, SmallInteger, Text
from sqlalchemy.orm import relationship

from app.module.system.model.base import Base, TimestampMixin, TenantMixin


class User(Base, TimestampMixin, TenantMixin):
    """用户表"""

    __tablename__ = "system_users"

    # 基本信息
    username = Column(String(30), unique=True, nullable=False, comment="用户账号")
    password = Column(String(100), nullable=False, comment="密码")
    nickname = Column(String(30), nullable=False, comment="用户昵称")
    avatar = Column(String(512), nullable=True, comment="头像地址")
    email = Column(String(50), nullable=True, comment="邮箱")
    mobile = Column(String(11), nullable=True, comment="手机号码")
    sex = Column(SmallInteger, default=0, comment="性别: 0-未知, 1-男, 2-女")

    # 状态
    status = Column(SmallInteger, default=0, comment="状态: 0-正常, 1-禁用")

    # 部门和岗位
    dept_id = Column(BigInteger, nullable=True, comment="部门ID")
    post_ids = Column(String(255), nullable=True, comment="岗位ID列表，逗号分隔")

    # 登录信息
    login_ip = Column(String(50), nullable=True, comment="最后登录IP")
    login_date = Column(DateTime, nullable=True, comment="最后登录时间")

    # 扩展信息
    remark = Column(String(500), nullable=True, comment="备注")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, nickname={self.nickname})>"

    @property
    def is_active(self) -> bool:
        """是否激活"""
        return self.status == 0

    @property
    def is_admin(self) -> bool:
        """是否是管理员"""
        return self.id == 1

    def get_post_ids_list(self) -> List[int]:
        """获取岗位ID列表"""
        if not self.post_ids:
            return []
        return [int(pid) for pid in self.post_ids.split(",") if pid]


class UserRole(Base):
    """用户-角色关联表"""

    __tablename__ = "system_user_role"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, comment="用户ID")
    role_id = Column(BigInteger, nullable=False, comment="角色ID")


class UserPost(Base):
    """用户-岗位关联表"""

    __tablename__ = "system_user_post"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, default=0, comment="用户ID")
    post_id = Column(BigInteger, nullable=False, default=0, comment="岗位ID")
    creator = Column(String(64), nullable=True, default="", comment="创建者")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    updater = Column(String(64), nullable=True, default="", comment="更新者")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    deleted = Column(Integer, default=0, comment="是否删除: 0-未删除, 1-已删除")
    tenant_id = Column(BigInteger, default=0, index=True, comment="租户编号")