"""
AI 工具服务
参考 ruoyi-vue-pro yudao-module-ai 模块的 AiToolService
"""
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.ai.model.tool import Tool
from app.module.ai.schema.tool import (
    AiToolCreate,
    AiToolUpdate,
    AiToolPageQuery,
)
from app.core.exceptions import BusinessException


# AI 工具错误码
class AiToolErrorCode:
    """AI 工具错误码定义"""

    # AI 工具 1-040-010-000
    TOOL_NOT_EXISTS = 1040010000
    TOOL_NAME_NOT_EXISTS = 1040010001


class AiToolService:
    """AI 工具服务类"""

    @staticmethod
    async def get_by_id(db: AsyncSession, tool_id: int) -> Optional[Tool]:
        """根据ID获取工具"""
        result = await db.execute(
            select(Tool).where(Tool.id == tool_id, Tool.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(db: AsyncSession, query: AiToolPageQuery) -> Tuple[List[Tool], int]:
        """分页查询工具列表"""
        # 构建查询条件
        conditions = [Tool.deleted == 0]

        if query.name:
            conditions.append(Tool.name.like(f"%{query.name}%"))
        if query.description:
            conditions.append(Tool.description.like(f"%{query.description}%"))
        if query.status is not None:
            conditions.append(Tool.status == query.status)

        # 查询总数
        count_query = select(func.count()).select_from(Tool).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        result = await db.execute(
            select(Tool)
            .where(and_(*conditions))
            .order_by(Tool.id.desc())
            .offset(query.offset)
            .limit(query.limit)
        )
        tools = result.scalars().all()

        return list(tools), total

    @staticmethod
    async def get_list_by_status(db: AsyncSession, status: int) -> List[Tool]:
        """根据状态获取工具列表"""
        result = await db.execute(
            select(Tool)
            .where(Tool.deleted == 0, Tool.status == status)
            .order_by(Tool.id.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, tool_create: AiToolCreate) -> Tool:
        """创建工具"""
        # 创建工具
        tool = Tool(
            name=tool_create.name,
            description=tool_create.description,
            status=tool_create.status,
        )

        db.add(tool)
        await db.flush()
        await db.refresh(tool)

        return tool

    @staticmethod
    async def update(db: AsyncSession, tool_id: int, tool_update: AiToolUpdate) -> Tool:
        """更新工具"""
        tool = await AiToolService.get_by_id(db, tool_id)
        if not tool:
            raise BusinessException(
                code=AiToolErrorCode.TOOL_NOT_EXISTS,
                message="工具不存在"
            )

        # 更新字段
        update_data = tool_update.model_dump(exclude_unset=True, exclude={"id"})
        for key, value in update_data.items():
            if hasattr(tool, key):
                setattr(tool, key, value)

        await db.flush()
        await db.refresh(tool)

        return tool

    @staticmethod
    async def delete(db: AsyncSession, tool_id: int) -> bool:
        """删除工具（软删除）"""
        tool = await AiToolService.get_by_id(db, tool_id)
        if not tool:
            raise BusinessException(
                code=AiToolErrorCode.TOOL_NOT_EXISTS,
                message="工具不存在"
            )

        tool.deleted = 1
        await db.flush()

        return True

    @staticmethod
    async def validate_tool_exists(db: AsyncSession, tool_id: int) -> Tool:
        """验证工具是否存在"""
        tool = await AiToolService.get_by_id(db, tool_id)
        if not tool:
            raise BusinessException(
                code=AiToolErrorCode.TOOL_NOT_EXISTS,
                message="工具不存在"
            )
        return tool