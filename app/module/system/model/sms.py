"""
短信模型
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, BigInteger, SmallInteger, Text

from app.module.system.model.base import Base, TimestampMixin, TenantMixin


class SmsChannel(Base, TimestampMixin):
    """短信渠道表"""

    __tablename__ = "system_sms_channel"

    signature = Column(String(12), nullable=False, comment="短信签名")
    code = Column(String(63), nullable=False, comment="渠道编码")
    status = Column(SmallInteger, nullable=False, comment="状态")
    remark = Column(String(255), nullable=True, comment="备注")
    api_key = Column(String(128), nullable=False, comment="短信API的账号")
    api_secret = Column(String(128), nullable=True, comment="短信API的密钥")
    callback_url = Column(String(255), nullable=True, comment="短信发送回调URL")


class SmsTemplate(Base, TimestampMixin):
    """短信模板表"""

    __tablename__ = "system_sms_template"

    name = Column(String(63), nullable=False, comment="模板名称")
    code = Column(String(63), nullable=False, comment="模板编码")
    channel_id = Column(BigInteger, nullable=False, comment="短信渠道编号")
    channel_code = Column(String(63), nullable=False, comment="短信渠道编码")
    content = Column(String(500), nullable=False, comment="模板内容")
    params = Column(String(255), nullable=False, comment="参数数组")
    status = Column(SmallInteger, nullable=False, comment="状态")
    remark = Column(String(255), nullable=True, comment="备注")


class SmsLog(Base, TimestampMixin):
    """短信日志表"""

    __tablename__ = "system_sms_log"

    channel_id = Column(BigInteger, nullable=False, comment="短信渠道编号")
    channel_code = Column(String(63), nullable=False, comment="短信渠道编码")
    template_id = Column(BigInteger, nullable=False, comment="模板编号")
    template_code = Column(String(63), nullable=False, comment="模板编码")
    template_type = Column(SmallInteger, nullable=False, comment="模板类型")
    template_content = Column(String(500), nullable=False, comment="模板内容")
    template_params = Column(String(255), nullable=False, comment="模板参数")
    mobile = Column(String(11), nullable=False, comment="手机号")
    user_id = Column(BigInteger, nullable=True, comment="用户编号")
    user_type = Column(SmallInteger, nullable=True, comment="用户类型")
    send_status = Column(SmallInteger, nullable=False, default=0, comment="发送状态")
    send_time = Column(DateTime, nullable=True, comment="发送时间")
    api_code = Column(Integer, nullable=True, comment="API发送编码")
    api_msg = Column(String(255), nullable=True, comment="API发送信息")
    api_request_id = Column(String(255), nullable=True, comment="API请求ID")
    receive_status = Column(SmallInteger, nullable=False, default=0, comment="接收状态")
    receive_time = Column(DateTime, nullable=True, comment="接收时间")


class SmsCode(Base, TenantMixin):
    """短信验证码表"""

    __tablename__ = "system_sms_code"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    mobile = Column(String(11), nullable=False, comment="手机号")
    code = Column(String(6), nullable=False, comment="验证码")
    create_ip = Column(String(15), nullable=False, comment="创建IP")
    scene = Column(SmallInteger, nullable=False, comment="发送场景")
    today_index = Column(Integer, nullable=False, comment="今日发送序号")
    used = Column(SmallInteger, nullable=False, default=0, comment="是否使用: 0-未使用, 1-已使用")
    used_time = Column(DateTime, nullable=True, comment="使用时间")
    used_ip = Column(String(15), nullable=True, comment="使用IP")
    creator = Column(String(64), nullable=True, default="", comment="创建者")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    updater = Column(String(64), nullable=True, default="", comment="更新者")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    deleted = Column(Integer, default=0, comment="是否删除: 0-未删除, 1-已删除")