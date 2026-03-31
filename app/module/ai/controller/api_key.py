"""
AI API 密钥控制器
参考 ruoyi-vue-pro yudao-module-ai 模块的 AiApiKeyController
"""
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import check_permission
from app.module.system.model.user import User
from app.module.ai.service.api_key import ApiKeyService
from app.module.ai.schema.api_key import (
    ApiKeyCreate,
    ApiKeyUpdate,
    ApiKeyResponse,
    ApiKeySimpleResponse,
    ApiKeyPageQuery,
)
from app.common.response import success, page_success
from app.common.decorators import operate_log

router = APIRouter()


@router.post("/create", summary="创建 API 密钥")
@operate_log(type="AI API 密钥管理", sub_type="创建 API 密钥")
async def create_api_key(
    request: Request,
    key_create: ApiKeyCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:api-key:create")),
):
    """创建 API 密钥"""
    key = await ApiKeyService.create(db, key_create)
    return success(data=key.id)


@router.put("/update", summary="更新 API 密钥")
@operate_log(type="AI API 密钥管理", sub_type="更新 API 密钥")
async def update_api_key(
    request: Request,
    key_update: ApiKeyUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:api-key:update")),
):
    """更新 API 密钥"""
    await ApiKeyService.update(db, key_update.id, key_update)
    return success(data=True)


@router.delete("/delete", summary="删除 API 密钥")
@operate_log(type="AI API 密钥管理", sub_type="删除 API 密钥")
async def delete_api_key(
    request: Request,
    id: int = Query(..., description="API 密钥编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:api-key:delete")),
):
    """删除 API 密钥"""
    await ApiKeyService.delete(db, id)
    return success(data=True)


@router.get("/get", summary="获得 API 密钥")
async def get_api_key(
    id: int = Query(..., description="API 密钥编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:api-key:query")),
):
    """根据 ID 获取 API 密钥详情"""
    key = await ApiKeyService.get_by_id(db, id)
    if not key:
        return success(data=None)
    return success(data=ApiKeyResponse.model_validate(key))


@router.get("/page", summary="获得 API 密钥分页")
async def get_api_key_page(
    query: ApiKeyPageQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:api-key:query")),
):
    """分页查询 API 密钥列表"""
    keys, total = await ApiKeyService.get_list(db, query)
    key_responses = [ApiKeyResponse.model_validate(k) for k in keys]
    return page_success(
        list_data=key_responses,
        total=total,
        page_no=query.page_no,
        page_size=query.page_size,
    )


@router.get("/simple-list", summary="获得 API 密钥精简列表")
async def get_api_key_simple_list(
    db: AsyncSession = Depends(get_db),
):
    """获得 API 密钥精简列表（用于前端下拉选项）"""
    keys = await ApiKeyService.get_all_list(db)
    simple_responses = [
        ApiKeySimpleResponse(id=k.id, name=k.name)
        for k in keys
    ]
    return success(data=simple_responses)