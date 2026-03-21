"""
OAuth2 模型
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, BigInteger, SmallInteger, Text, Index

from app.module.system.model.base import Base, TimestampMixin, TenantMixin, SoftDeleteMixin


class OAuth2Client(Base, TimestampMixin, SoftDeleteMixin):
    """OAuth2 客户端表"""

    __tablename__ = "system_oauth2_client"

    client_id = Column(String(255), nullable=False, comment="客户端编号")
    secret = Column(String(255), nullable=False, comment="客户端密钥")
    name = Column(String(255), nullable=False, comment="应用名")
    logo = Column(String(255), nullable=True, comment="应用图标")
    description = Column(String(255), nullable=True, comment="应用描述")
    status = Column(SmallInteger, default=0, comment="状态: 0-正常, 1-禁用")
    access_token_validity_seconds = Column(Integer, nullable=False, default=86400, comment="访问令牌的有效期")
    refresh_token_validity_seconds = Column(Integer, nullable=False, default=2592000, comment="刷新令牌的有效期")
    redirect_uris = Column(String(255), nullable=True, comment="可重定向的URI地址")
    authorized_grant_types = Column(String(255), nullable=True, comment="授权类型")
    scopes = Column(String(255), nullable=True, comment="授权范围")
    auto_approve_scopes = Column(String(255), nullable=True, comment="自动通过的授权范围")
    authorities = Column(String(255), nullable=True, comment="权限")
    resource_ids = Column(String(255), nullable=True, comment="资源")
    additional_information = Column(String(4096), nullable=True, comment="附加信息")


class OAuth2AccessToken(Base, TimestampMixin, TenantMixin):
    """OAuth2 访问令牌表"""

    __tablename__ = "system_oauth2_access_token"

    user_id = Column(BigInteger, nullable=False, comment="用户编号")
    user_type = Column(SmallInteger, nullable=False, comment="用户类型")
    user_info = Column(String(512), nullable=False, comment="用户信息")
    access_token = Column(String(255), nullable=False, comment="访问令牌")
    refresh_token = Column(String(32), nullable=False, comment="刷新令牌")
    client_id = Column(String(255), nullable=False, comment="客户端编号")
    scopes = Column(String(255), nullable=True, comment="授权范围")
    expires_time = Column(DateTime, nullable=False, comment="过期时间")

    __table_args__ = (
        Index('idx_access_token', 'access_token'),
        Index('idx_refresh_token', 'refresh_token'),
    )


class OAuth2RefreshToken(Base, TimestampMixin, TenantMixin):
    """OAuth2 刷新令牌表"""

    __tablename__ = "system_oauth2_refresh_token"

    user_id = Column(BigInteger, nullable=False, comment="用户编号")
    refresh_token = Column(String(32), nullable=False, comment="刷新令牌")
    user_type = Column(SmallInteger, nullable=False, comment="用户类型")
    client_id = Column(String(255), nullable=False, comment="客户端编号")
    scopes = Column(String(255), nullable=True, comment="授权范围")
    expires_time = Column(DateTime, nullable=False, comment="过期时间")


class OAuth2Code(Base, TimestampMixin, TenantMixin):
    """OAuth2 授权码表"""

    __tablename__ = "system_oauth2_code"

    user_id = Column(BigInteger, nullable=False, comment="用户编号")
    user_type = Column(SmallInteger, nullable=False, comment="用户类型")
    code = Column(String(32), nullable=False, comment="授权码")
    client_id = Column(String(255), nullable=False, comment="客户端编号")
    scopes = Column(String(255), nullable=True, default="", comment="授权范围")
    expires_time = Column(DateTime, nullable=False, comment="过期时间")
    redirect_uri = Column(String(255), nullable=True, comment="可重定向的URI地址")
    state = Column(String(255), nullable=False, default="", comment="状态")


class OAuth2Approve(Base, TimestampMixin, TenantMixin):
    """OAuth2 批准表"""

    __tablename__ = "system_oauth2_approve"

    user_id = Column(BigInteger, nullable=False, comment="用户编号")
    user_type = Column(SmallInteger, nullable=False, comment="用户类型")
    client_id = Column(String(255), nullable=False, comment="客户端编号")
    scope = Column(String(255), nullable=False, default="", comment="授权范围")
    approved = Column(SmallInteger, nullable=False, default=0, comment="是否接受")
    expires_time = Column(DateTime, nullable=False, comment="过期时间")