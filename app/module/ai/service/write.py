"""
AI 写作服务
参考 ruoyi-vue-pro yudao-module-ai 模块的 AiWriteService
"""
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.ai.model.write import Write
from app.module.ai.schema.write import (
    WritePageQuery,
    WriteGenerateReqVO,
)
from app.core.exceptions import BusinessException


class WriteErrorCode:
    """AI 写作错误码定义"""

    WRITE_NOT_EXISTS = 1040030000


class WriteService:
    """AI 写作服务类"""

    @staticmethod
    async def get_by_id(db: AsyncSession, write_id: int) -> Optional[Write]:
        """根据ID获取写作"""
        result = await db.execute(
            select(Write).where(Write.id == write_id, Write.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_page(db: AsyncSession, query: WritePageQuery) -> Tuple[List[Write], int]:
        """分页查询写作列表"""
        # 构建查询条件
        conditions = [Write.deleted == 0]

        if query.user_id:
            conditions.append(Write.user_id == query.user_id)
        if query.type is not None:
            conditions.append(Write.type == query.type)
        if query.platform:
            conditions.append(Write.platform == query.platform)

        # 查询总数
        count_query = select(func.count()).select_from(Write).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        result = await db.execute(
            select(Write)
            .where(and_(*conditions))
            .order_by(Write.id.desc())
            .offset(query.offset)
            .limit(query.limit)
        )
        writes = result.scalars().all()

        return list(writes), total

    @staticmethod
    async def delete(db: AsyncSession, write_id: int) -> bool:
        """删除写作"""
        write = await WriteService.get_by_id(db, write_id)
        if not write:
            raise BusinessException(
                code=WriteErrorCode.WRITE_NOT_EXISTS,
                message="写作不存在"
            )

        write.deleted = 1
        await db.flush()

        return True

    @staticmethod
    async def create_write(
        db: AsyncSession,
        user_id: int,
        platform: str,
        model_id: int,
        model: str,
        generate_req: WriteGenerateReqVO,
        generated_content: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> Write:
        """创建写作记录"""
        write = Write(
            user_id=user_id,
            type=generate_req.type,
            platform=platform,
            model_id=model_id,
            model=model,
            prompt=generate_req.prompt or "",
            generated_content=generated_content,
            original_content=generate_req.original_content,
            length=generate_req.length,
            format=generate_req.format,
            tone=generate_req.tone,
            language=generate_req.language,
            error_message=error_message,
        )

        db.add(write)
        await db.flush()
        await db.refresh(write)

        return write