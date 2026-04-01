"""
AI 思维导图服务
参考 ruoyi-vue-pro yudao-module-ai AiMindMapService
"""
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.ai.model.mind_map import MindMap
from app.module.ai.schema.mind_map import MindMapPageQuery
from app.core.exceptions import BusinessException


class MindMapService:
    """AI 思维导图服务类"""

    @staticmethod
    async def get_by_id(db: AsyncSession, mind_map_id: int) -> Optional[MindMap]:
        """根据ID获取思维导图"""
        result = await db.execute(
            select(MindMap).where(MindMap.id == mind_map_id, MindMap.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_page(
        db: AsyncSession,
        query: MindMapPageQuery
    ) -> Tuple[List[MindMap], int]:
        """分页查询思维导图列表"""
        # 构建查询条件
        conditions = [MindMap.deleted == 0]

        if query.user_id:
            conditions.append(MindMap.user_id == query.user_id)
        if query.prompt:
            conditions.append(MindMap.prompt.like(f"%{query.prompt}%"))
        if query.create_time and len(query.create_time) == 2:
            conditions.append(MindMap.create_time.between(query.create_time[0], query.create_time[1]))

        # 查询总数
        count_query = select(func.count()).select_from(MindMap).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        result = await db.execute(
            select(MindMap)
            .where(and_(*conditions))
            .order_by(MindMap.id.desc())
            .offset(query.offset)
            .limit(query.limit)
        )
        mind_maps = result.scalars().all()

        return list(mind_maps), total

    @staticmethod
    async def delete(db: AsyncSession, mind_map_id: int) -> bool:
        """删除思维导图（软删除）"""
        mind_map = await MindMapService.get_by_id(db, mind_map_id)
        if not mind_map:
            raise BusinessException(code=404, message="思维导图不存在")

        mind_map.deleted = 1
        await db.flush()
        return True