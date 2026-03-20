"""
文件模型
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, BigInteger, SmallInteger, Text

from app.module.infra.model.base import Base, TimestampMixin


class File(Base, TimestampMixin):
    """文件表"""

    __tablename__ = "infra_file"

    config_id = Column(BigInteger, nullable=True, comment="配置编号")
    name = Column(String(256), nullable=True, comment="文件名")
    path = Column(String(512), nullable=False, comment="文件路径")
    url = Column(String(1024), nullable=False, comment="文件URL")
    type = Column(String(128), nullable=True, comment="文件类型")
    size = Column(Integer, nullable=False, comment="文件大小")


class FileConfig(Base, TimestampMixin):
    """文件配置表"""

    __tablename__ = "infra_file_config"

    name = Column(String(63), nullable=False, comment="配置名")
    storage = Column(SmallInteger, nullable=False, comment="存储器")
    remark = Column(String(255), nullable=True, comment="备注")
    master = Column(SmallInteger, nullable=False, default=0, comment="是否为主配置")
    config = Column(String(4096), nullable=False, comment="存储配置")


class FileContent(Base, TimestampMixin):
    """文件内容表（数据库存储）"""

    __tablename__ = "infra_file_content"

    config_id = Column(BigInteger, nullable=False, comment="配置编号")
    path = Column(String(512), nullable=False, comment="文件路径")
    content = Column(Text, nullable=False, comment="文件内容")