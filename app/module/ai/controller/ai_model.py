"""
AI 模型控制器
参考 ruoyi-vue-pro yudao-module-ai 模块的 AiModelController
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import check_permission
from app.module.system.model.user import User
from app.module.ai.service.ai_model import AiModelService
from app.module.ai.schema.ai_model import (
    AiModelCreate,
    AiModelUpdate,
    AiModelResponse,
    AiModelSimpleResponse,
    AiModelPageQuery,
)
from app.common.response import success, page_success
from app.common.decorators import operate_log

router = APIRouter()


@router.post("/create", summary="创建模型")
@operate_log(type="AI 模型管理", sub_type="创建模型")
async def create_model(
    request: Request,
    model_create: AiModelCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:model:create")),
):
    """创建 AI 模型"""
    model = await AiModelService.create(db, model_create)
    return success(data=model.id)


@router.put("/update", summary="更新模型")
@operate_log(type="AI 模型管理", sub_type="更新模型")
async def update_model(
    request: Request,
    model_update: AiModelUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:model:update")),
):
    """更新 AI 模型"""
    await AiModelService.update(db, model_update.id, model_update)
    return success(data=True)


@router.delete("/delete", summary="删除模型")
@operate_log(type="AI 模型管理", sub_type="删除模型")
async def delete_model(
    request: Request,
    id: int = Query(..., description="模型编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:model:delete")),
):
    """删除 AI 模型"""
    await AiModelService.delete(db, id)
    return success(data=True)


@router.get("/get", summary="获得模型")
async def get_model(
    id: int = Query(..., description="模型编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:model:query")),
):
    """根据 ID 获取模型详情"""
    model = await AiModelService.get_by_id(db, id)
    if not model:
        return success(data=None)
    return success(data=AiModelResponse.model_validate(model))


@router.get("/page", summary="获得模型分页")
async def get_model_page(
    query: AiModelPageQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:model:query")),
):
    """分页查询模型列表"""
    models, total = await AiModelService.get_list(db, query)
    model_responses = [AiModelResponse.model_validate(m) for m in models]
    return page_success(
        list_data=model_responses,
        total=total,
        page_no=query.page_no,
        page_size=query.page_size,
    )


@router.get("/simple-list", summary="获得模型精简列表")
async def get_model_simple_list(
    type: int = Query(..., description="模型类型"),
    platform: Optional[str] = Query(None, description="模型平台"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:model:query")),
):
    """获得模型精简列表（用于前端下拉选项）"""
    # 状态为启用（0）的模型列表
    models = await AiModelService.get_list_by_status_and_type(
        db, status=0, type=type, platform=platform
    )
    simple_responses = [
        AiModelSimpleResponse(
            id=m.id,
            name=m.name,
            model=m.model,
            platform=m.platform,
        )
        for m in models
    ]
    return success(data=simple_responses)