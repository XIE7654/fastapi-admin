"""
AI 音乐服务
参考 ruoyi-vue-pro yudao-module-ai 模块的 AiMusicService
"""
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.ai.model.music import Music
from app.module.ai.schema.music import (
    MusicUpdate,
    MusicUpdateMy,
    MusicPageQuery,
)
from app.core.exceptions import BusinessException


class MusicErrorCode:
    """音乐错误码定义"""

    MUSIC_NOT_EXISTS = 1040030000


class MusicService:
    """AI 音乐服务类"""

    @staticmethod
    async def get_by_id(db: AsyncSession, music_id: int) -> Optional[Music]:
        """根据ID获取音乐"""
        result = await db.execute(
            select(Music).where(Music.id == music_id, Music.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(db: AsyncSession, query: MusicPageQuery) -> Tuple[List[Music], int]:
        """分页查询音乐列表"""
        # 构建查询条件
        conditions = [Music.deleted == 0]

        if query.user_id:
            conditions.append(Music.user_id == query.user_id)
        if query.title:
            conditions.append(Music.title.like(f"%{query.title}%"))
        if query.status:
            conditions.append(Music.status == query.status)
        if query.generate_mode:
            conditions.append(Music.generate_mode == query.generate_mode)
        if query.public_status is not None:
            conditions.append(Music.public_status == (1 if query.public_status else 0))

        # 查询总数
        count_query = select(func.count()).select_from(Music).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        result = await db.execute(
            select(Music)
            .where(and_(*conditions))
            .order_by(Music.id.desc())
            .offset(query.offset)
            .limit(query.limit)
        )
        musics = result.scalars().all()

        return list(musics), total

    @staticmethod
    async def get_my_list(db: AsyncSession, query: MusicPageQuery, user_id: int) -> Tuple[List[Music], int]:
        """分页查询【我的】音乐列表"""
        # 构建查询条件
        conditions = [Music.deleted == 0, Music.user_id == user_id]

        if query.title:
            conditions.append(Music.title.like(f"%{query.title}%"))
        if query.status:
            conditions.append(Music.status == query.status)
        if query.generate_mode:
            conditions.append(Music.generate_mode == query.generate_mode)
        if query.public_status is not None:
            conditions.append(Music.public_status == (1 if query.public_status else 0))

        # 查询总数
        count_query = select(func.count()).select_from(Music).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        result = await db.execute(
            select(Music)
            .where(and_(*conditions))
            .order_by(Music.id.desc())
            .offset(query.offset)
            .limit(query.limit)
        )
        musics = result.scalars().all()

        return list(musics), total

    @staticmethod
    async def update_my(db: AsyncSession, music_update: MusicUpdateMy, user_id: int) -> Music:
        """更新【我的】音乐"""
        music = await MusicService.get_by_id(db, music_update.id)
        if not music:
            raise BusinessException(
                code=MusicErrorCode.MUSIC_NOT_EXISTS,
                message="音乐不存在"
            )
        if music.user_id != user_id:
            raise BusinessException(
                code=MusicErrorCode.MUSIC_NOT_EXISTS,
                message="无权限修改该音乐"
            )

        music.title = music_update.title
        await db.flush()
        await db.refresh(music)

        return music

    @staticmethod
    async def update(db: AsyncSession, music_update: MusicUpdate) -> Music:
        """更新音乐（管理端）"""
        music = await MusicService.get_by_id(db, music_update.id)
        if not music:
            raise BusinessException(
                code=MusicErrorCode.MUSIC_NOT_EXISTS,
                message="音乐不存在"
            )

        update_data = music_update.model_dump(exclude_unset=True, exclude={"id"})
        for key, value in update_data.items():
            if hasattr(music, key):
                setattr(music, key, value)

        await db.flush()
        await db.refresh(music)

        return music

    @staticmethod
    async def delete(db: AsyncSession, music_id: int) -> bool:
        """删除音乐（软删除）"""
        music = await MusicService.get_by_id(db, music_id)
        if not music:
            raise BusinessException(
                code=MusicErrorCode.MUSIC_NOT_EXISTS,
                message="音乐不存在"
            )

        music.deleted = 1
        await db.flush()

        return True

    @staticmethod
    async def delete_my(db: AsyncSession, music_id: int, user_id: int) -> bool:
        """删除【我的】音乐"""
        music = await MusicService.get_by_id(db, music_id)
        if not music:
            raise BusinessException(
                code=MusicErrorCode.MUSIC_NOT_EXISTS,
                message="音乐不存在"
            )
        if music.user_id != user_id:
            raise BusinessException(
                code=MusicErrorCode.MUSIC_NOT_EXISTS,
                message="无权限删除该音乐"
            )

        music.deleted = 1
        await db.flush()

        return True