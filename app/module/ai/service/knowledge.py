"""
AI 知识库服务
参考 ruoyi-vue-pro yudao-module-ai AiKnowledgeService
"""
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.ai.model.knowledge import Knowledge
from app.module.ai.schema.knowledge import (
    KnowledgeCreate,
    KnowledgeUpdate,
    KnowledgePageQuery,
)
from app.core.exceptions import BusinessException


class KnowledgeErrorCode:
    """AI 知识库错误码定义"""
    KNOWLEDGE_NOT_EXISTS = 1040009000


class KnowledgeService:
    """AI 知识库服务类"""

    @staticmethod
    async def get_by_id(db: AsyncSession, knowledge_id: int) -> Optional[Knowledge]:
        """根据ID获取知识库"""
        result = await db.execute(
            select(Knowledge).where(Knowledge.id == knowledge_id, Knowledge.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_page(
        db: AsyncSession,
        query: KnowledgePageQuery
    ) -> Tuple[List[Knowledge], int]:
        """分页查询知识库列表"""
        # 构建查询条件
        conditions = [Knowledge.deleted == 0]

        if query.name:
            conditions.append(Knowledge.name.like(f"%{query.name}%"))
        if query.status is not None:
            conditions.append(Knowledge.status == query.status)

        # 查询总数
        count_query = select(func.count()).select_from(Knowledge).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        result = await db.execute(
            select(Knowledge)
            .where(and_(*conditions))
            .order_by(Knowledge.id.desc())
            .offset(query.offset)
            .limit(query.limit)
        )
        knowledge_list = result.scalars().all()

        return list(knowledge_list), total

    @staticmethod
    async def get_list_by_status(db: AsyncSession, status: int) -> List[Knowledge]:
        """根据状态获取知识库列表"""
        result = await db.execute(
            select(Knowledge)
            .where(Knowledge.deleted == 0, Knowledge.status == status)
            .order_by(Knowledge.id.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, knowledge_create: KnowledgeCreate) -> Knowledge:
        """创建知识库"""
        knowledge = Knowledge(
            name=knowledge_create.name,
            description=knowledge_create.description,
            embedding_model_id=knowledge_create.embedding_model_id,
            embedding_model=knowledge_create.embedding_model,
            top_k=knowledge_create.top_k,
            similarity_threshold=knowledge_create.similarity_threshold,
            status=knowledge_create.status,
        )

        db.add(knowledge)
        await db.flush()
        await db.refresh(knowledge)

        return knowledge

    @staticmethod
    async def update(
        db: AsyncSession,
        knowledge_id: int,
        knowledge_update: KnowledgeUpdate
    ) -> Knowledge:
        """更新知识库"""
        knowledge = await KnowledgeService.get_by_id(db, knowledge_id)
        if not knowledge:
            raise BusinessException(
                code=KnowledgeErrorCode.KNOWLEDGE_NOT_EXISTS,
                message="知识库不存在"
            )

        # 更新字段
        update_data = knowledge_update.model_dump(exclude_unset=True, exclude={"id"})
        for key, value in update_data.items():
            if hasattr(knowledge, key):
                setattr(knowledge, key, value)

        await db.flush()
        await db.refresh(knowledge)

        return knowledge

    @staticmethod
    async def delete(db: AsyncSession, knowledge_id: int) -> bool:
        """删除知识库（软删除）"""
        knowledge = await KnowledgeService.get_by_id(db, knowledge_id)
        if not knowledge:
            raise BusinessException(
                code=KnowledgeErrorCode.KNOWLEDGE_NOT_EXISTS,
                message="知识库不存在"
            )

        knowledge.deleted = 1
        await db.flush()

        return True

    @staticmethod
    async def validate_knowledge_exists(db: AsyncSession, knowledge_id: int) -> Knowledge:
        """验证知识库是否存在"""
        knowledge = await KnowledgeService.get_by_id(db, knowledge_id)
        if not knowledge:
            raise BusinessException(
                code=KnowledgeErrorCode.KNOWLEDGE_NOT_EXISTS,
                message="知识库不存在"
            )
        return knowledge