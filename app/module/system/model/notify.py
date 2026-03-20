"""
站内信模板模型
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, BigInteger, SmallInteger, Text

from app.module.system.model.base import Base, TimestampMixin


class NotifyTemplate(Base, TimestampMixin):
    """站内信模板表"""

    __tablename__ = "system_notify_template"

    name = Column(String(63), nullable=False, comment="模板名称")
    code = Column(String(64), nullable=False, comment="模版编码")
    nickname = Column(String(255), nullable=False, comment="发送人名称")
    content = Column(String(1024), nullable=False, comment="模版内容")
    type = Column(SmallInteger, nullable=False, comment="类型")
    params = Column(String(255), nullable=True, comment="参数数组")
    status = Column(SmallInteger, nullable=False, comment="状态")
    remark = Column(String(255), nullable=True, comment="备注")


class NotifyMessage(Base, TimestampMixin):
    """站内信消息表"""

    __tablename__ = "system_notify_message"

    user_id = Column(BigInteger, nullable=False, comment="用户id")
    user_type = Column(SmallInteger, nullable=False, comment="用户类型")
    template_id = Column(BigInteger, nullable=False, comment="模版编号")
    template_code = Column(String(64), nullable=False, comment="模板编码")
    template_nickname = Column(String(63), nullable=False, comment="模版发送人名称")
    template_content = Column(String(1024), nullable=False, comment="模版内容")
    template_type = Column(Integer, nullable=False, comment="模版类型")
    template_params = Column(String(255), nullable=False, comment="模版参数")
    read_status = Column(SmallInteger, nullable=False, default=0, comment="是否已读: 0-未读, 1-已读")
    read_time = Column(DateTime, nullable=True, comment="阅读时间")