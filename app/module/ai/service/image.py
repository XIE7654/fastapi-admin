"""
AI 绘画服务
参考 ruoyi-vue-pro yudao-module-ai 模块的 AiImageService
"""
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.ai.model.image import Image
from app.module.ai.schema.image import (
    ImagePageQuery,
    ImageUpdate,
    ImageDrawReqVO,
)
from app.core.exceptions import BusinessException


class ImageErrorCode:
    """AI 绘画错误码定义"""

    IMAGE_NOT_EXISTS = 1040020000
    IMAGE_STATUS_ERROR = 1040020001


class ImageService:
    """AI 绘画服务类"""

    @staticmethod
    async def get_by_id(db: AsyncSession, image_id: int) -> Optional[Image]:
        """根据ID获取绘画"""
        result = await db.execute(
            select(Image).where(Image.id == image_id, Image.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list_by_ids(db: AsyncSession, ids: List[int]) -> List[Image]:
        """根据ID列表获取绘画列表"""
        if not ids:
            return []
        result = await db.execute(
            select(Image).where(Image.id.in_(ids), Image.deleted == 0)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_page(db: AsyncSession, query: ImagePageQuery) -> Tuple[List[Image], int]:
        """分页查询绘画列表（管理端）"""
        # 构建查询条件
        conditions = [Image.deleted == 0]

        if query.user_id:
            conditions.append(Image.user_id == query.user_id)
        if query.platform:
            conditions.append(Image.platform == query.platform)
        if query.prompt:
            conditions.append(Image.prompt.like(f"%{query.prompt}%"))
        if query.status is not None:
            conditions.append(Image.status == query.status)
        if query.public_status is not None:
            conditions.append(Image.public_status == query.public_status)

        # 查询总数
        count_query = select(func.count()).select_from(Image).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        result = await db.execute(
            select(Image)
            .where(and_(*conditions))
            .order_by(Image.id.desc())
            .offset(query.offset)
            .limit(query.limit)
        )
        images = result.scalars().all()

        return list(images), total

    @staticmethod
    async def get_page_my(
        db: AsyncSession,
        user_id: int,
        query: ImagePageQuery
    ) -> Tuple[List[Image], int]:
        """分页查询【我的】绘画列表"""
        # 构建查询条件
        conditions = [Image.deleted == 0, Image.user_id == user_id]

        if query.platform:
            conditions.append(Image.platform == query.platform)
        if query.prompt:
            conditions.append(Image.prompt.like(f"%{query.prompt}%"))
        if query.status is not None:
            conditions.append(Image.status == query.status)

        # 查询总数
        count_query = select(func.count()).select_from(Image).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        result = await db.execute(
            select(Image)
            .where(and_(*conditions))
            .order_by(Image.id.desc())
            .offset(query.offset)
            .limit(query.limit)
        )
        images = result.scalars().all()

        return list(images), total

    @staticmethod
    async def get_page_public(db: AsyncSession, query: ImagePageQuery) -> Tuple[List[Image], int]:
        """分页查询公开绘画列表"""
        # 构建查询条件
        conditions = [Image.deleted == 0, Image.public_status == 1]

        if query.platform:
            conditions.append(Image.platform == query.platform)
        if query.prompt:
            conditions.append(Image.prompt.like(f"%{query.prompt}%"))

        # 查询总数
        count_query = select(func.count()).select_from(Image).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        result = await db.execute(
            select(Image)
            .where(and_(*conditions))
            .order_by(Image.id.desc())
            .offset(query.offset)
            .limit(query.limit)
        )
        images = result.scalars().all()

        return list(images), total

    @staticmethod
    async def update(db: AsyncSession, image_id: int, image_update: ImageUpdate) -> Image:
        """更新绘画"""
        image = await ImageService.get_by_id(db, image_id)
        if not image:
            raise BusinessException(
                code=ImageErrorCode.IMAGE_NOT_EXISTS,
                message="绘画不存在"
            )

        # 更新字段
        update_data = image_update.model_dump(exclude_unset=True, exclude={"id"})
        for key, value in update_data.items():
            if hasattr(image, key):
                setattr(image, key, value)

        await db.flush()
        await db.refresh(image)

        return image

    @staticmethod
    async def delete(db: AsyncSession, image_id: int) -> bool:
        """删除绘画（管理端）"""
        image = await ImageService.get_by_id(db, image_id)
        if not image:
            raise BusinessException(
                code=ImageErrorCode.IMAGE_NOT_EXISTS,
                message="绘画不存在"
            )

        image.deleted = 1
        await db.flush()

        return True

    @staticmethod
    async def delete_my(db: AsyncSession, image_id: int, user_id: int) -> bool:
        """删除【我的】绘画"""
        image = await ImageService.get_by_id(db, image_id)
        if not image:
            raise BusinessException(
                code=ImageErrorCode.IMAGE_NOT_EXISTS,
                message="绘画不存在"
            )

        if image.user_id != user_id:
            raise BusinessException(
                code=ImageErrorCode.IMAGE_NOT_EXISTS,
                message="绘画不存在"
            )

        image.deleted = 1
        await db.flush()

        return True

    @staticmethod
    async def draw_image(
        db: AsyncSession,
        user_id: int,
        draw_req: ImageDrawReqVO
    ) -> int:
        """生成图片"""
        image = Image(
            user_id=user_id,
            platform=draw_req.platform,
            model=draw_req.model or "",
            prompt=draw_req.prompt,
            width=draw_req.width,
            height=draw_req.height,
            status=10,  # 进行中
            options=draw_req.options,
            public_status=0,
        )

        db.add(image)
        await db.flush()
        await db.refresh(image)

        return image.id