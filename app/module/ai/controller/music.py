"""
AI 音乐控制器
参考 ruoyi-vue-pro yudao-module-ai 模块的 AiMusicController
"""
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import check_permission, get_current_user
from app.module.system.model.user import User
from app.module.ai.service.music import MusicService
from app.module.ai.schema.music import (
    MusicUpdate,
    MusicUpdateMy,
    MusicResponse,
    MusicPageQuery,
)
from app.common.response import success, page_success
from app.common.decorators import operate_log

router = APIRouter()


@router.get("/page", summary="获得音乐分页")
async def get_music_page(
    query: MusicPageQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:music:query")),
):
    """分页查询音乐列表"""
    musics, total = await MusicService.get_list(db, query)
    music_responses = [MusicResponse.model_validate(m) for m in musics]
    return page_success(
        list_data=music_responses,
        total=total,
        page_no=query.page_no,
        page_size=query.page_size,
    )


@router.get("/my-page", summary="获得【我的】音乐分页")
async def get_music_my_page(
    query: MusicPageQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """分页查询【我的】音乐列表"""
    musics, total = await MusicService.get_my_list(db, query, current_user.id)
    music_responses = [MusicResponse.model_validate(m) for m in musics]
    return page_success(
        list_data=music_responses,
        total=total,
        page_no=query.page_no,
        page_size=query.page_size,
    )


@router.get("/get", summary="获得音乐")
async def get_music(
    id: int = Query(..., description="音乐编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:music:query")),
):
    """根据 ID 获取音乐详情"""
    music = await MusicService.get_by_id(db, id)
    if not music:
        return success(data=None)
    return success(data=MusicResponse.model_validate(music))


@router.get("/get-my", summary="获得【我的】音乐")
async def get_music_my(
    id: int = Query(..., description="音乐编号"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """根据 ID 获取【我的】音乐详情"""
    music = await MusicService.get_by_id(db, id)
    if not music or music.user_id != current_user.id:
        return success(data=None)
    return success(data=MusicResponse.model_validate(music))


@router.put("/update", summary="更新音乐")
@operate_log(type="AI 音乐管理", sub_type="更新音乐")
async def update_music(
    request: Request,
    music_update: MusicUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:music:update")),
):
    """更新音乐"""
    await MusicService.update(db, music_update)
    return success(data=True)


@router.put("/update-my", summary="更新【我的】音乐")
@operate_log(type="AI 音乐管理", sub_type="更新我的音乐")
async def update_music_my(
    request: Request,
    music_update: MusicUpdateMy,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新【我的】音乐"""
    await MusicService.update_my(db, music_update, current_user.id)
    return success(data=True)


@router.delete("/delete", summary="删除音乐")
@operate_log(type="AI 音乐管理", sub_type="删除音乐")
async def delete_music(
    request: Request,
    id: int = Query(..., description="音乐编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:music:delete")),
):
    """删除音乐"""
    await MusicService.delete(db, id)
    return success(data=True)


@router.delete("/delete-my", summary="删除【我的】音乐")
@operate_log(type="AI 音乐管理", sub_type="删除我的音乐")
async def delete_music_my(
    request: Request,
    id: int = Query(..., description="音乐编号"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除【我的】音乐"""
    await MusicService.delete_my(db, id, current_user.id)
    return success(data=True)