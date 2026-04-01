"""
AI 工作流服务
参考 ruoyi-vue-pro yudao-module-ai 模块的 AiWorkflowService
"""
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.ai.model.workflow import Workflow
from app.module.ai.schema.workflow import (
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowPageQuery,
)
from app.core.exceptions import BusinessException


class WorkflowErrorCode:
    """工作流错误码定义"""

    WORKFLOW_NOT_EXISTS = 1040040000


class WorkflowService:
    """AI 工作流服务类"""

    @staticmethod
    async def get_by_id(db: AsyncSession, workflow_id: int) -> Optional[Workflow]:
        """根据ID获取工作流"""
        result = await db.execute(
            select(Workflow).where(Workflow.id == workflow_id, Workflow.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(db: AsyncSession, query: WorkflowPageQuery) -> Tuple[List[Workflow], int]:
        """分页查询工作流列表"""
        # 构建查询条件
        conditions = [Workflow.deleted == 0]

        if query.name:
            conditions.append(Workflow.name.like(f"%{query.name}%"))
        if query.code:
            conditions.append(Workflow.code.like(f"%{query.code}%"))
        if query.status:
            conditions.append(Workflow.status == query.status)

        # 查询总数
        count_query = select(func.count()).select_from(Workflow).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        result = await db.execute(
            select(Workflow)
            .where(and_(*conditions))
            .order_by(Workflow.id.desc())
            .offset(query.offset)
            .limit(query.limit)
        )
        workflows = result.scalars().all()

        return list(workflows), total

    @staticmethod
    async def create(db: AsyncSession, workflow_create: WorkflowCreate) -> Workflow:
        """创建工作流"""
        workflow = Workflow(
            code=workflow_create.code,
            name=workflow_create.name,
            graph=workflow_create.graph,
            status=workflow_create.status,
            remark=workflow_create.remark,
        )

        db.add(workflow)
        await db.flush()
        await db.refresh(workflow)

        return workflow

    @staticmethod
    async def update(db: AsyncSession, workflow_id: int, workflow_update: WorkflowUpdate) -> Workflow:
        """更新工作流"""
        workflow = await WorkflowService.get_by_id(db, workflow_id)
        if not workflow:
            raise BusinessException(
                code=WorkflowErrorCode.WORKFLOW_NOT_EXISTS,
                message="工作流不存在"
            )

        update_data = workflow_update.model_dump(exclude_unset=True, exclude={"id"})
        for key, value in update_data.items():
            if hasattr(workflow, key):
                setattr(workflow, key, value)

        await db.flush()
        await db.refresh(workflow)

        return workflow

    @staticmethod
    async def delete(db: AsyncSession, workflow_id: int) -> bool:
        """删除工作流（软删除）"""
        workflow = await WorkflowService.get_by_id(db, workflow_id)
        if not workflow:
            raise BusinessException(
                code=WorkflowErrorCode.WORKFLOW_NOT_EXISTS,
                message="工作流不存在"
            )

        workflow.deleted = 1
        await db.flush()

        return True