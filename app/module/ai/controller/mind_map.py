"""
AI 思维导图控制器
参考 ruoyi-vue-pro yudao-module-ai AiMindMapController
"""
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import check_permission
from app.module.system.model.user import User
from app.module.ai.service.mind_map import MindMapService
from app.module.ai.schema.mind_map import (
    MindMapResponse,
    MindMapPageQuery,
)
from app.common.response import success, page_success
from app.common.decorators import operate_log

router = APIRouter()


@router.get("/page", summary="获得思维导图分页")
async def get_mind_map_page(
    query: MindMapPageQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:mind-map:query")),
):
    """分页查询思维导图列表"""
    mind_maps, total = await MindMapService.get_page(db, query)
    mind_map_responses = [MindMapResponse.model_validate(m) for m in mind_maps]
    return page_success(
        list_data=mind_map_responses,
        total=total,
        page_no=query.page_no,
        page_size=query.page_size,
    )


@router.delete("/delete", summary="删除思维导图")
@operate_log(type="AI 思维导图管理", sub_type="删除思维导图")
async def delete_mind_map(
    request: Request,
    id: int = Query(..., description="编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:mind-map:delete")),
):
    """删除思维导图"""
    await MindMapService.delete(db, id)
    return success(data=True)