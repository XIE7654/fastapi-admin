"""
AI 模型服务
"""
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.ai.model.ai_model import AiModel
from app.module.ai.schema.ai_model import (
    AiModelCreate,
    AiModelUpdate,
    AiModelPageQuery,
    AiPlatformEnum,
    AiModelTypeEnum,
)
from app.core.exceptions import BusinessException


# AI 模块错误码
class AiErrorCode:
    """AI 错误码定义"""

    # API 密钥 1-040-000-000
    API_KEY_NOT_EXISTS = 1040000000
    API_KEY_DISABLE = 1040000001

    # API 模型 1-040-001-000
    MODEL_NOT_EXISTS = 1040001000
    MODEL_DISABLE = 1040001001
    MODEL_DEFAULT_NOT_EXISTS = 1040001002
    MODEL_USE_TYPE_ERROR = 1040001003


class AiModelService:
    """AI 模型服务类"""

    @staticmethod
    async def get_by_id(db: AsyncSession, model_id: int) -> Optional[AiModel]:
        """根据ID获取模型"""
        result = await db.execute(
            select(AiModel).where(AiModel.id == model_id, AiModel.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(db: AsyncSession, query: AiModelPageQuery) -> Tuple[List[AiModel], int]:
        """分页查询模型列表"""
        # 构建查询条件
        conditions = [AiModel.deleted == 0]

        if query.name:
            conditions.append(AiModel.name.like(f"%{query.name}%"))
        if query.model:
            conditions.append(AiModel.model.like(f"%{query.model}%"))
        if query.platform:
            conditions.append(AiModel.platform == query.platform)

        # 查询总数
        count_query = select(func.count()).select_from(AiModel).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        result = await db.execute(
            select(AiModel)
            .where(and_(*conditions))
            .order_by(AiModel.sort.asc(), AiModel.id.desc())
            .offset(query.offset)
            .limit(query.limit)
        )
        models = result.scalars().all()

        return list(models), total

    @staticmethod
    async def get_list_by_status_and_type(
        db: AsyncSession,
        status: int,
        type: int,
        platform: Optional[str] = None
    ) -> List[AiModel]:
        """根据状态和类型获取模型列表"""
        conditions = [
            AiModel.deleted == 0,
            AiModel.status == status,
            AiModel.type == type
        ]
        if platform:
            conditions.append(AiModel.platform == platform)

        result = await db.execute(
            select(AiModel)
            .where(and_(*conditions))
            .order_by(AiModel.sort.asc(), AiModel.id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, model_create: AiModelCreate) -> AiModel:
        """创建模型"""
        # 验证平台
        try:
            AiPlatformEnum(model_create.platform)
        except ValueError:
            raise BusinessException(
                code=AiErrorCode.MODEL_USE_TYPE_ERROR,
                message=f"非法平台: {model_create.platform}"
            )

        # 验证模型类型
        try:
            AiModelTypeEnum(model_create.type)
        except ValueError:
            raise BusinessException(
                code=AiErrorCode.MODEL_USE_TYPE_ERROR,
                message=f"非法模型类型: {model_create.type}"
            )

        # 创建模型
        model = AiModel(
            key_id=model_create.key_id,
            name=model_create.name,
            model=model_create.model,
            platform=model_create.platform,
            type=model_create.type,
            sort=model_create.sort,
            status=model_create.status,
            temperature=model_create.temperature,
            max_tokens=model_create.max_tokens,
            max_contexts=model_create.max_contexts,
        )

        db.add(model)
        await db.flush()
        await db.refresh(model)

        return model

    @staticmethod
    async def update(db: AsyncSession, model_id: int, model_update: AiModelUpdate) -> AiModel:
        """更新模型"""
        model = await AiModelService.get_by_id(db, model_id)
        if not model:
            raise BusinessException(
                code=AiErrorCode.MODEL_NOT_EXISTS,
                message="模型不存在"
            )

        # 更新字段
        update_data = model_update.model_dump(exclude_unset=True, exclude={"id"})

        # 验证平台
        if "platform" in update_data and update_data["platform"]:
            try:
                AiPlatformEnum(update_data["platform"])
            except ValueError:
                raise BusinessException(
                    code=AiErrorCode.MODEL_USE_TYPE_ERROR,
                    message=f"非法平台: {update_data['platform']}"
                )

        # 验证模型类型
        if "type" in update_data and update_data["type"]:
            try:
                AiModelTypeEnum(update_data["type"])
            except ValueError:
                raise BusinessException(
                    code=AiErrorCode.MODEL_USE_TYPE_ERROR,
                    message=f"非法模型类型: {update_data['type']}"
                )

        for key, value in update_data.items():
            if hasattr(model, key):
                setattr(model, key, value)

        await db.flush()
        await db.refresh(model)

        return model

    @staticmethod
    async def delete(db: AsyncSession, model_id: int) -> bool:
        """删除模型（软删除）"""
        model = await AiModelService.get_by_id(db, model_id)
        if not model:
            raise BusinessException(
                code=AiErrorCode.MODEL_NOT_EXISTS,
                message="模型不存在"
            )

        model.deleted = 1
        await db.flush()

        return True

    @staticmethod
    async def validate_model(db: AsyncSession, model_id: int) -> AiModel:
        """验证模型是否可用"""
        model = await AiModelService.get_by_id(db, model_id)
        if not model:
            raise BusinessException(
                code=AiErrorCode.MODEL_NOT_EXISTS,
                message="模型不存在"
            )

        if model.status != 0:
            raise BusinessException(
                code=AiErrorCode.MODEL_DISABLE,
                message=f"模型({model.name})已禁用"
            )

        return model

    @staticmethod
    async def get_required_default_model(db: AsyncSession, type: int) -> AiModel:
        """获取默认模型（启用状态的第一个）"""
        result = await db.execute(
            select(AiModel)
            .where(
                AiModel.deleted == 0,
                AiModel.status == 0,
                AiModel.type == type
            )
            .order_by(AiModel.sort.asc())
            .limit(1)
        )
        model = result.scalar_one_or_none()

        if not model:
            raise BusinessException(
                code=AiErrorCode.MODEL_DEFAULT_NOT_EXISTS,
                message="操作失败，找不到默认模型"
            )

        return model