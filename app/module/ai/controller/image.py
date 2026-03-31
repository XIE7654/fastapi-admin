"""
AI 绘画控制器
参考 ruoyi-vue-pro yudao-module-ai 模块的 AiImageController
"""
from typing import List
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import check_permission
from app.core.user_context import get_user_id
from app.module.system.model.user import User
from app.module.ai.service.image import ImageService
from app.module.ai.schema.image import (
    ImagePageQuery,
    ImageUpdate,
    ImageResponse,
    ImageDrawReqVO,
)
from app.common.response import success, page_success
from app.common.decorators import operate_log

router = APIRouter()


# ================ 用户端接口 ================

@router.get("/my-page", summary="获取【我的】绘图分页")
async def get_image_page_my(
    query: ImagePageQuery = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """获取【我的】绘图分页"""
    user_id = get_user_id()
    images, total = await ImageService.get_page_my(db, user_id, query)
    image_responses = [ImageResponse.model_validate(img) for img in images]
    return page_success(
        list_data=image_responses,
        total=total,
        page_no=query.page_no,
        page_size=query.page_size,
    )


@router.get("/public-page", summary="获取公开的绘图分页")
async def get_image_page_public(
    query: ImagePageQuery = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """获取公开的绘图分页"""
    images, total = await ImageService.get_page_public(db, query)
    image_responses = [ImageResponse.model_validate(img) for img in images]
    return page_success(
        list_data=image_responses,
        total=total,
        page_no=query.page_no,
        page_size=query.page_size,
    )


@router.get("/get-my", summary="获取【我的】绘图记录")
async def get_image_my(
    id: int = Query(..., description="绘画编号"),
    db: AsyncSession = Depends(get_db),
):
    """获取【我的】绘图记录"""
    user_id = get_user_id()
    image = await ImageService.get_by_id(db, id)
    if not image or image.user_id != user_id:
        return success(data=None)
    return success(data=ImageResponse.model_validate(image))


@router.get("/my-list-by-ids", summary="获取【我的】绘图记录列表")
async def get_image_list_my_by_ids(
    ids: str = Query(..., description="绘画编号数组，逗号分隔"),
    db: AsyncSession = Depends(get_db),
):
    """获取【我的】绘图记录列表"""
    user_id = get_user_id()
    id_list = [int(x) for x in ids.split(",") if x.strip()]
    images = await ImageService.get_list_by_ids(db, id_list)
    # 过滤只属于自己的
    my_images = [img for img in images if img.user_id == user_id]
    image_responses = [ImageResponse.model_validate(img) for img in my_images]
    return success(data=image_responses)


@router.post("/draw", summary="生成图片")
async def draw_image(
    request: Request,
    draw_req: ImageDrawReqVO,
    db: AsyncSession = Depends(get_db),
):
    """生成图片"""
    user_id = get_user_id()
    image_id = await ImageService.draw_image(db, user_id, draw_req)
    return success(data=image_id)


@router.delete("/delete-my", summary="删除【我的】绘画记录")
async def delete_image_my(
    id: int = Query(..., description="绘画编号"),
    db: AsyncSession = Depends(get_db),
):
    """删除【我的】绘画记录"""
    user_id = get_user_id()
    await ImageService.delete_my(db, id, user_id)
    return success(data=True)


# ================ 管理端接口 ================

@router.get("/page", summary="获得绘画分页")
async def get_image_page(
    query: ImagePageQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:image:query")),
):
    """分页查询绘画列表（管理端）"""
    images, total = await ImageService.get_page(db, query)
    image_responses = [ImageResponse.model_validate(img) for img in images]
    return page_success(
        list_data=image_responses,
        total=total,
        page_no=query.page_no,
        page_size=query.page_size,
    )


@router.put("/update", summary="更新绘画")
@operate_log(type="AI 绘画管理", sub_type="更新绘画")
async def update_image(
    request: Request,
    image_update: ImageUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:image:update")),
):
    """更新绘画"""
    await ImageService.update(db, image_update.id, image_update)
    return success(data=True)


@router.delete("/delete", summary="删除绘画")
@operate_log(type="AI 绘画管理", sub_type="删除绘画")
async def delete_image(
    request: Request,
    id: int = Query(..., description="绘画编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:image:delete")),
):
    """删除绘画"""
    await ImageService.delete(db, id)
    return success(data=True)