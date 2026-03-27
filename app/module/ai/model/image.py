"""
AI 绘画模型
"""
from sqlalchemy import Column, String, BigInteger, Integer, SmallInteger, DateTime, Text
from sqlalchemy.dialects.mysql import JSON

from app.module.system.model.base import Base, TimestampMixin, TenantMixin


class Image(Base, TimestampMixin, TenantMixin):
    """AI 绘画表"""

    __tablename__ = "ai_image"

    user_id = Column(BigInteger, nullable=False, comment="用户编号")
    prompt = Column(String(2000), nullable=False, comment="提示词")
    platform = Column(String(64), nullable=False, comment="平台")
    model_id = Column(BigInteger, nullable=True, comment="模型编号")
    model = Column(String(64), nullable=False, comment="模型")
    width = Column(Integer, nullable=False, comment="图片宽度")
    height = Column(Integer, nullable=False, comment="图片高度")
    status = Column(SmallInteger, nullable=False, comment="绘画状态")
    finish_time = Column(DateTime, nullable=True, comment="完成时间")
    error_message = Column(String(1024), nullable=True, comment="错误信息")
    public_status = Column(SmallInteger, default=0, comment="是否发布: 0-否, 1-是")
    pic_url = Column(String(2048), nullable=True, comment="图片地址")
    options = Column(JSON, nullable=True, comment="绘制参数")
    task_id = Column(String(1024), nullable=True, comment="任务编号")
    buttons = Column(String(2048), nullable=True, comment="mj buttons 按钮")

    def __repr__(self):
        return f"<Image(id={self.id}, prompt={self.prompt[:20]}...)>"