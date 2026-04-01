"""
AI 知识库控制器
参考 ruoyi-vue-pro yudao-module-ai AiKnowledgeController
"""
from typing import List
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import check_permission
from app.module.system.model.user import User
from app.module.ai.service.knowledge import KnowledgeService
from app.module.ai.schema.knowledge import (
    KnowledgeCreate,
    KnowledgeUpdate,
    KnowledgeResponse,
    KnowledgeSimpleResponse,
    KnowledgePageQuery,
)
from app.common.response import success, page_success
from app.common.decorators import operate_log

router = APIRouter()


@router.get("/page", summary="获得知识库分页")
async def get_knowledge_page(
    query: KnowledgePageQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:knowledge:query")),
):
    """分页查询知识库列表"""
    knowledge_list, total = await KnowledgeService.get_page(db, query)
    knowledge_responses = [KnowledgeResponse.model_validate(k) for k in knowledge_list]
    return page_success(
        list_data=knowledge_responses,
        total=total,
        page_no=query.page_no,
        page_size=query.page_size,
    )


@router.get("/get", summary="获得知识库")
async def get_knowledge(
    id: int = Query(..., description="知识库编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:knowledge:query")),
):
    """根据ID获取知识库详情"""
    knowledge = await KnowledgeService.get_by_id(db, id)
    if not knowledge:
        return success(data=None)
    return success(data=KnowledgeResponse.model_validate(knowledge))


@router.post("/create", summary="创建知识库")
@operate_log(type="AI 知识库管理", sub_type="创建知识库")
async def create_knowledge(
    request: Request,
    knowledge_create: KnowledgeCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:knowledge:create")),
):
    """创建知识库"""
    knowledge = await KnowledgeService.create(db, knowledge_create)
    return success(data=knowledge.id)


@router.put("/update", summary="更新知识库")
@operate_log(type="AI 知识库管理", sub_type="更新知识库")
async def update_knowledge(
    request: Request,
    knowledge_update: KnowledgeUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:knowledge:update")),
):
    """更新知识库"""
    await KnowledgeService.update(db, knowledge_update.id, knowledge_update)
    return success(data=True)


@router.delete("/delete", summary="删除知识库")
@operate_log(type="AI 知识库管理", sub_type="删除知识库")
async def delete_knowledge(
    request: Request,
    id: int = Query(..., description="知识库编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:knowledge:delete")),
):
    """删除知识库"""
    await KnowledgeService.delete(db, id)
    return success(data=True)


@router.get("/simple-list", summary="获得知识库精简列表")
async def get_knowledge_simple_list(
    db: AsyncSession = Depends(get_db),
):
    """获得知识库精简列表（用于前端下拉选项，只返回启用状态的知识库）"""
    # 状态为启用（0）的知识库列表
    knowledge_list = await KnowledgeService.get_list_by_status(db, status=0)
    simple_responses = [
        KnowledgeSimpleResponse(
            id=k.id,
            name=k.name,
        )
        for k in knowledge_list
    ]
    return success(data=simple_responses)