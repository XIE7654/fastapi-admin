"""
AI 模型表
"""
from sqlalchemy import Column, String, BigInteger, Integer, SmallInteger, Float

from app.module.system.model.base import Base, TimestampMixin, TenantMixin


class AiModel(Base, TimestampMixin, TenantMixin):
    """AI 模型表"""

    __tablename__ = "ai_model"

    key_id = Column(BigInteger, nullable=False, comment="API 秘钥编号")
    name = Column(String(64), nullable=False, comment="模型名字")
    model = Column(String(64), nullable=False, comment="模型标识")
    platform = Column(String(32), nullable=False, comment="模型平台")
    type = Column(SmallInteger, nullable=False, comment="模型类型")
    sort = Column(Integer, nullable=False, comment="排序")
    status = Column(SmallInteger, nullable=False, comment="状态")
    temperature = Column(Float, nullable=True, comment="温度参数")
    max_tokens = Column(Integer, nullable=True, comment="单条回复的最大 Token 数量")
    max_contexts = Column(Integer, nullable=True, comment="上下文的最大 Message 数量")

    def __repr__(self):
        return f"<AiModel(id={self.id}, name={self.name}, model={self.model})>"