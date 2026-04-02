"""
AI 绘画服务
参考 ruoyi-vue-pro yudao-module-ai 模块的 AiImageService
"""
import base64
import logging
from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.ai.model.image import Image
from app.module.ai.model.ai_model import AiModel
from app.module.ai.model.api_key import ApiKey
from app.module.ai.schema.image import (
    ImagePageQuery,
    ImageUpdate,
    ImageDrawReqVO,
)
from app.module.ai.service.image_client import ImageClient, ImageStatusEnum
from app.core.exceptions import BusinessException

logger = logging.getLogger(__name__)


class ImageErrorCode:
    """AI 绘画错误码定义"""

    IMAGE_NOT_EXISTS = 1040020000
    IMAGE_STATUS_ERROR = 1040020001
    MODEL_NOT_EXISTS = 1040020002
    API_KEY_NOT_EXISTS = 1040020003


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
        """
        生成图片
        创建数据库记录并返回 ID，异步执行绘图任务
        """
        import asyncio
        from app.core.database import async_session_maker

        # 1. 校验模型
        model = await ImageService._get_model(db, draw_req.model_id)
        if not model:
            raise BusinessException(
                code=ImageErrorCode.MODEL_NOT_EXISTS,
                message="模型不存在"
            )

        # 2. 获取 API Key
        api_key = await ImageService._get_api_key(db, model.key_id)
        if not api_key:
            raise BusinessException(
                code=ImageErrorCode.API_KEY_NOT_EXISTS,
                message="API密钥不存在"
            )

        # 3. 创建数据库记录
        image = Image(
            user_id=user_id,
            platform=model.platform,  # 使用模型的平台
            model_id=model.id,
            model=model.model,
            prompt=draw_req.prompt,
            width=draw_req.width,
            height=draw_req.height,
            status=ImageStatusEnum.IN_PROGRESS,  # 进行中
            options=draw_req.options,
            public_status=0,
        )

        db.add(image)
        await db.flush()
        await db.refresh(image)

        image_id = image.id

        # 4. 异步执行绘图任务
        asyncio.create_task(
            ImageService._execute_draw_image(
                image_id=image_id,
                platform=model.platform,
                model_name=model.model,
                prompt=draw_req.prompt,
                width=draw_req.width,
                height=draw_req.height,
                options=draw_req.options,
                api_key=api_key.api_key,
                base_url=api_key.url,
            )
        )

        return image_id

    @staticmethod
    async def _get_model(db: AsyncSession, model_id: Optional[int]) -> Optional[AiModel]:
        """获取模型"""
        if not model_id:
            # 获取默认图片模型
            result = await db.execute(
                select(AiModel)
                .where(AiModel.deleted == 0, AiModel.status == 0, AiModel.type == 2)  # type=2 图片
                .order_by(AiModel.sort.asc())
                .limit(1)
            )
            return result.scalar_one_or_none()

        result = await db.execute(
            select(AiModel).where(AiModel.id == model_id, AiModel.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def _get_api_key(db: AsyncSession, key_id: int) -> Optional[ApiKey]:
        """获取 API Key"""
        result = await db.execute(
            select(ApiKey).where(ApiKey.id == key_id, ApiKey.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def _execute_draw_image(
        image_id: int,
        platform: str,
        model_name: str,
        prompt: str,
        width: int,
        height: int,
        options: Optional[dict],
        api_key: str,
        base_url: Optional[str],
    ):
        """
        异步执行绘图任务
        """
        from app.core.database import async_session_maker

        async with async_session_maker() as db:
            try:
                # 1. 调用 AI 绘图 API
                client = ImageClient(api_key=api_key, base_url=base_url)
                result = await client.generate_image(
                    platform=platform,
                    model=model_name,
                    prompt=prompt,
                    width=width,
                    height=height,
                    options=options,
                )

                # 2. 处理结果
                if result.get("error"):
                    # 失败
                    await ImageService._update_image_status(
                        db, image_id,
                        status=ImageStatusEnum.FAIL,
                        error_message=result["error"]
                    )
                else:
                    # 成功
                    pic_url = None

                    # 如果有 base64 数据，保存到文件服务
                    if result.get("b64_json"):
                        pic_url = await ImageService._save_image_to_file(
                            db, result["b64_json"], image_id
                        )
                    elif result.get("url"):
                        pic_url = result["url"]

                    await ImageService._update_image_status(
                        db, image_id,
                        status=ImageStatusEnum.SUCCESS,
                        pic_url=pic_url
                    )

            except Exception as e:
                logger.error(f"[execute_draw_image] image_id={image_id} 绘图异常: {e}")
                await ImageService._update_image_status(
                    db, image_id,
                    status=ImageStatusEnum.FAIL,
                    error_message=str(e)
                )

    @staticmethod
    async def _save_image_to_file(db: AsyncSession, b64_json: str, image_id: int) -> Optional[str]:
        """
        保存图片到文件服务
        返回 base64 数据 URL，实际项目中应该上传到文件服务器
        """
        # 返回完整的 base64 数据 URL
        return f"data:image/png;base64,{b64_json}"

    @staticmethod
    async def _update_image_status(
        db: AsyncSession,
        image_id: int,
        status: int,
        pic_url: Optional[str] = None,
        error_message: Optional[str] = None,
    ):
        """更新图片状态"""
        result = await db.execute(
            select(Image).where(Image.id == image_id, Image.deleted == 0)
        )
        image = result.scalar_one_or_none()

        if image:
            image.status = status
            image.finish_time = datetime.now()
            if pic_url:
                image.pic_url = pic_url
            if error_message:
                image.error_message = error_message

            await db.commit()