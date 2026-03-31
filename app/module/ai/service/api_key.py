"""
AI API 密钥服务
参考 ruoyi-vue-pro yudao-module-ai 模块的 AiApiKeyService
"""
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.ai.model.api_key import ApiKey
from app.module.ai.schema.api_key import (
    ApiKeyCreate,
    ApiKeyUpdate,
    ApiKeyPageQuery,
)
from app.core.exceptions import BusinessException


class ApiKeyErrorCode:
    """API 密钥错误码定义"""

    API_KEY_NOT_EXISTS = 1040000000
    API_KEY_DISABLE = 1040000001


class ApiKeyService:
    """API 密钥服务类"""

    @staticmethod
    async def get_by_id(db: AsyncSession, key_id: int) -> Optional[ApiKey]:
        """根据ID获取API密钥"""
        result = await db.execute(
            select(ApiKey).where(ApiKey.id == key_id, ApiKey.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(db: AsyncSession, query: ApiKeyPageQuery) -> Tuple[List[ApiKey], int]:
        """分页查询API密钥列表"""
        # 构建查询条件
        conditions = [ApiKey.deleted == 0]

        if query.name:
            conditions.append(ApiKey.name.like(f"%{query.name}%"))
        if query.platform:
            conditions.append(ApiKey.platform == query.platform)
        if query.status is not None:
            conditions.append(ApiKey.status == query.status)

        # 查询总数
        count_query = select(func.count()).select_from(ApiKey).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        result = await db.execute(
            select(ApiKey)
            .where(and_(*conditions))
            .order_by(ApiKey.id.desc())
            .offset(query.offset)
            .limit(query.limit)
        )
        keys = result.scalars().all()

        return list(keys), total

    @staticmethod
    async def get_all_list(db: AsyncSession) -> List[ApiKey]:
        """获取所有API密钥列表"""
        result = await db.execute(
            select(ApiKey)
            .where(ApiKey.deleted == 0)
            .order_by(ApiKey.id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, key_create: ApiKeyCreate) -> ApiKey:
        """创建API密钥"""
        key = ApiKey(
            name=key_create.name,
            api_key=key_create.api_key,
            platform=key_create.platform,
            url=key_create.url,
            status=key_create.status,
        )

        db.add(key)
        await db.flush()
        await db.refresh(key)

        return key

    @staticmethod
    async def update(db: AsyncSession, key_id: int, key_update: ApiKeyUpdate) -> ApiKey:
        """更新API密钥"""
        key = await ApiKeyService.get_by_id(db, key_id)
        if not key:
            raise BusinessException(
                code=ApiKeyErrorCode.API_KEY_NOT_EXISTS,
                message="API密钥不存在"
            )

        # 更新字段
        update_data = key_update.model_dump(exclude_unset=True, exclude={"id"})
        for key_name, value in update_data.items():
            if hasattr(key, key_name):
                setattr(key, key_name, value)

        await db.flush()
        await db.refresh(key)

        return key

    @staticmethod
    async def delete(db: AsyncSession, key_id: int) -> bool:
        """删除API密钥（软删除）"""
        key = await ApiKeyService.get_by_id(db, key_id)
        if not key:
            raise BusinessException(
                code=ApiKeyErrorCode.API_KEY_NOT_EXISTS,
                message="API密钥不存在"
            )

        key.deleted = 1
        await db.flush()

        return True

    @staticmethod
    async def validate_api_key(db: AsyncSession, key_id: int) -> ApiKey:
        """验证API密钥是否可用"""
        key = await ApiKeyService.get_by_id(db, key_id)
        if not key:
            raise BusinessException(
                code=ApiKeyErrorCode.API_KEY_NOT_EXISTS,
                message="API密钥不存在"
            )

        if key.status != 0:
            raise BusinessException(
                code=ApiKeyErrorCode.API_KEY_DISABLE,
                message=f"API密钥({key.name})已禁用"
            )

        return key

    @staticmethod
    async def get_required_default_api_key(
        db: AsyncSession,
        platform: Optional[str] = None,
        status: int = 0
    ) -> ApiKey:
        """获取默认API密钥"""
        conditions = [ApiKey.deleted == 0, ApiKey.status == status]
        if platform:
            conditions.append(ApiKey.platform == platform)

        result = await db.execute(
            select(ApiKey)
            .where(and_(*conditions))
            .order_by(ApiKey.id.asc())
            .limit(1)
        )
        key = result.scalar_one_or_none()

        if not key:
            raise BusinessException(
                code=ApiKeyErrorCode.API_KEY_NOT_EXISTS,
                message="找不到默认API密钥"
            )

        return key