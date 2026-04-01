"""
AI 工作流控制器
参考 ruoyi-vue-pro yudao-module-ai 模块的 AiWorkflowController
"""
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import check_permission
from app.module.system.model.user import User
from app.module.ai.service.workflow import WorkflowService
from app.module.ai.schema.workflow import (
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowResponse,
    WorkflowPageQuery,
)
from app.common.response import success, page_success
from app.common.decorators import operate_log

router = APIRouter()


@router.post("/create", summary="创建 AI 工作流")
@operate_log(type="AI 工作流管理", sub_type="创建工作流")
async def create_workflow(
    request: Request,
    workflow_create: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:workflow:create")),
):
    """创建 AI 工作流"""
    workflow = await WorkflowService.create(db, workflow_create)
    return success(data=workflow.id)


@router.put("/update", summary="更新 AI 工作流")
@operate_log(type="AI 工作流管理", sub_type="更新工作流")
async def update_workflow(
    request: Request,
    workflow_update: WorkflowUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:workflow:update")),
):
    """更新 AI 工作流"""
    await WorkflowService.update(db, workflow_update.id, workflow_update)
    return success(data=True)


@router.delete("/delete", summary="删除 AI 工作流")
@operate_log(type="AI 工作流管理", sub_type="删除工作流")
async def delete_workflow(
    request: Request,
    id: int = Query(..., description="工作流编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:workflow:delete")),
):
    """删除 AI 工作流"""
    await WorkflowService.delete(db, id)
    return success(data=True)


@router.get("/get", summary="获得 AI 工作流")
async def get_workflow(
    id: int = Query(..., description="工作流编号"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:workflow:query")),
):
    """根据 ID 获取工作流详情"""
    workflow = await WorkflowService.get_by_id(db, id)
    if not workflow:
        return success(data=None)
    return success(data=WorkflowResponse.model_validate(workflow))


@router.get("/page", summary="获得 AI 工作流分页")
async def get_workflow_page(
    query: WorkflowPageQuery = Depends(),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_permission("ai:workflow:query")),
):
    """分页查询工作流列表"""
    workflows, total = await WorkflowService.get_list(db, query)
    workflow_responses = [WorkflowResponse.model_validate(w) for w in workflows]
    return page_success(
        list_data=workflow_responses,
        total=total,
        page_no=query.page_no,
        page_size=query.page_size,
    )