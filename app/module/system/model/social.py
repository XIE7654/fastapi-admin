"""
社交登录模型
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, BigInteger, SmallInteger, Text

from app.module.system.model.base import Base, TimestampMixin, TenantMixin


class SocialClient(Base, TimestampMixin):
    """社交客户端表"""

    __tablename__ = "system_social_client"

    name = Column(String(63), nullable=False, comment="应用名")
    social_type = Column(SmallInteger, nullable=False, comment="社交类型")
    user_type = Column(SmallInteger, nullable=False, comment="用户类型")
    client_id = Column(String(255), nullable=False, comment="客户端ID")
    client_secret = Column(String(255), nullable=False, comment="客户端密钥")
    agent_id = Column(String(64), nullable=True, comment="代理编号")
    status = Column(SmallInteger, nullable=False, comment="状态")
    remark = Column(String(255), nullable=True, comment="备注")


class SocialUser(Base, TimestampMixin):
    """社交用户表"""

    __tablename__ = "system_social_user"

    type = Column(SmallInteger, nullable=False, comment="社交类型")
    openid = Column(String(64), nullable=False, comment="社交openid")
    token = Column(String(256), nullable=True, comment="社交token")
    raw_token_info = Column(String(1024), nullable=True, comment="原始Token数据")
    nickname = Column(String(32), nullable=True, comment="用户昵称")
    avatar = Column(String(255), nullable=True, comment="用户头像")
    raw_user_info = Column(String(1024), nullable=True, comment="原始用户数据")


class SocialUserBind(Base, TimestampMixin, TenantMixin):
    """社交绑定表"""

    __tablename__ = "system_social_user_bind"

    user_id = Column(BigInteger, nullable=False, comment="用户编号")
    user_type = Column(SmallInteger, nullable=False, comment="用户类型")
    social_type = Column(SmallInteger, nullable=False, comment="社交平台的类型")
    social_user_id = Column(BigInteger, nullable=False, comment="社交用户的编号")