"""
AI 音乐模型
"""
from sqlalchemy import Column, String, BigInteger, SmallInteger, Float, Integer

from app.module.system.model.base import Base, TimestampMixin, TenantMixin


class Music(Base, TimestampMixin, TenantMixin):
    """AI 音乐表"""

    __tablename__ = "ai_music"

    user_id = Column(BigInteger, nullable=False, comment="用户编号")
    title = Column(String(200), nullable=False, comment="音乐名称")
    lyric = Column(String(2048), nullable=True, comment="歌词")
    image_url = Column(String(600), nullable=True, comment="图片地址")
    audio_url = Column(String(600), nullable=True, comment="音频地址")
    video_url = Column(String(600), nullable=True, comment="视频地址")
    status = Column(SmallInteger, nullable=False, comment="音乐状态")
    description = Column(String(2048), nullable=True, comment="描述词")
    prompt = Column(String(2048), nullable=True, comment="提示词")
    platform = Column(String(64), nullable=False, comment="模型平台")
    model_id = Column(BigInteger, nullable=False, comment="模型编号")
    model = Column(String(50), nullable=False, comment="模型")
    generate_mode = Column(SmallInteger, nullable=False, comment="生成模式")
    tags = Column(String(600), nullable=True, comment="音乐风格标签")
    duration = Column(Float, nullable=True, comment="音乐时长")
    public_status = Column(SmallInteger, default=0, comment="是否发布: 0-否, 1-是")
    task_id = Column(String(255), nullable=True, comment="任务编号")
    error_message = Column(String(1024), nullable=True, comment="错误信息")

    def __repr__(self):
        return f"<Music(id={self.id}, title={self.title})>"