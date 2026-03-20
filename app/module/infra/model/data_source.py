"""
数据源配置模型
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, BigInteger, SmallInteger

from app.module.infra.model.base import Base, TimestampMixin


class DataSourceConfig(Base, TimestampMixin):
    """数据源配置表"""

    __tablename__ = "infra_data_source_config"

    name = Column(String(100), nullable=False, default="", comment="参数名称")
    url = Column(String(1024), nullable=False, comment="数据源连接")
    username = Column(String(255), nullable=False, comment="用户名")
    password = Column(String(255), nullable=False, default="", comment="密码")