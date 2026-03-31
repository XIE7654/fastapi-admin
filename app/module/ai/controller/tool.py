"""
AI 工具控制器
参考 ruoyi-vue-pro yudao-module-ai 模块的 AiToolController
"""
from typing import List
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import check_permission
from app.module.system.model.user import User
from app.module.ai.service.tool import AiToolService
from app.module.ai.schema.tool import (
    AiToolCreate,
    AiToolUpdate,
    AiToolResponse,
    AiToolSimpleResponse,
    AiToolPageQuery,
)
from app.common.response import success, page_success
from app.common.decorators import operate_log

router = APIRouter()


@router.post("/create", summary="创建工具")
@operate_log(type="AI 工具管理", sub_type="创建工具")
async def create_tool(
    request: Request,
    tool_create: AiToolCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:tool:create")),
):
    """创建 AI 工具"""
    tool = await AiToolService.create(db, tool_create)
    return success(data=tool.id)


@router.put("/update", summary="更新工具")
@operate_log(type="AI 工具管理", sub_type="更新工具")
async def update_tool(
    request: Request,
    tool_update: AiToolUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:tool:update")),
):
    """更新 AI 工具"""
    await AiToolService.update(db, tool_update.id, tool_update)
    return success(data=True)


@router.delete("/delete", summary="删除工具")
@operate_log(type="AI 工具管理", sub_type="删除工具")
async def delete_tool(
    request: Request,
    id: int = Query(..., description="工具编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:tool:delete")),
):
    """删除 AI 工具"""
    await AiToolService.delete(db, id)
    return success(data=True)


@router.get("/get", summary="获得工具")
async def get_tool(
    id: int = Query(..., description="工具编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:tool:query")),
):
    """根据 ID 获取工具详情"""
    tool = await AiToolService.get_by_id(db, id)
    if not tool:
        return success(data=None)
    return success(data=AiToolResponse.model_validate(tool))


@router.get("/page", summary="获得工具分页")
async def get_tool_page(
    query: AiToolPageQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:tool:query")),
):
    """分页查询工具列表"""
    tools, total = await AiToolService.get_list(db, query)
    tool_responses = [AiToolResponse.model_validate(t) for t in tools]
    return page_success(
        list_data=tool_responses,
        total=total,
        page_no=query.page_no,
        page_size=query.page_size,
    )


@router.get("/simple-list", summary="获得工具精简列表")
async def get_tool_simple_list(
    db: AsyncSession = Depends(get_db),
):
    """获得工具精简列表（用于前端下拉选项，只返回启用状态的工具）"""
    # 状态为启用（0）的工具列表
    tools = await AiToolService.get_list_by_status(db, status=0)
    simple_responses = [
        AiToolSimpleResponse(
            id=t.id,
            name=t.name,
        )
        for t in tools
    ]
    return success(data=simple_responses)