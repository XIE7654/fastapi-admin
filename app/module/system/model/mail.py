"""
邮件模型
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, BigInteger, SmallInteger, Text, Boolean

from app.module.system.model.base import Base, TimestampMixin


class MailAccount(Base, TimestampMixin):
    """邮箱账号表"""

    __tablename__ = "system_mail_account"

    mail = Column(String(255), nullable=False, comment="邮箱")
    username = Column(String(255), nullable=False, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码")
    host = Column(String(255), nullable=False, comment="SMTP服务器域名")
    port = Column(Integer, nullable=False, comment="SMTP服务器端口")
    ssl_enable = Column(SmallInteger, nullable=False, default=0, comment="是否开启SSL")
    starttls_enable = Column(SmallInteger, nullable=False, default=0, comment="是否开启STARTTLS")


class MailTemplate(Base, TimestampMixin):
    """邮件模版表"""

    __tablename__ = "system_mail_template"

    name = Column(String(63), nullable=False, comment="模板名称")
    code = Column(String(63), nullable=False, comment="模板编码")
    account_id = Column(BigInteger, nullable=False, comment="发送的邮箱账号编号")
    nickname = Column(String(255), nullable=True, comment="发送人名称")
    title = Column(String(255), nullable=False, comment="模板标题")
    content = Column(String(10240), nullable=False, comment="模板内容")
    params = Column(String(255), nullable=False, comment="参数数组")
    status = Column(SmallInteger, nullable=False, comment="开启状态")
    remark = Column(String(255), nullable=True, comment="备注")


class MailLog(Base, TimestampMixin):
    """邮件日志表"""

    __tablename__ = "system_mail_log"

    user_id = Column(BigInteger, nullable=True, comment="用户编号")
    user_type = Column(SmallInteger, nullable=True, comment="用户类型")
    to_mails = Column(String(1024), nullable=False, comment="接收邮箱地址")
    cc_mails = Column(String(1024), nullable=True, comment="抄送邮箱地址")
    bcc_mails = Column(String(1024), nullable=True, comment="密送邮箱地址")
    account_id = Column(BigInteger, nullable=False, comment="邮箱账号编号")
    from_mail = Column(String(255), nullable=False, comment="发送邮箱地址")
    template_id = Column(BigInteger, nullable=False, comment="模板编号")
    template_code = Column(String(63), nullable=False, comment="模板编码")
    template_nickname = Column(String(255), nullable=True, comment="模版发送人名称")
    template_title = Column(String(255), nullable=False, comment="邮件标题")
    template_content = Column(Text, nullable=False, comment="邮件内容")
    template_params = Column(String(255), nullable=False, comment="邮件参数")
    send_status = Column(SmallInteger, nullable=False, default=0, comment="发送状态")
    send_time = Column(DateTime, nullable=True, comment="发送时间")
    send_message_id = Column(String(255), nullable=True, comment="发送返回的消息ID")
    send_exception = Column(String(4096), nullable=True, comment="发送异常")