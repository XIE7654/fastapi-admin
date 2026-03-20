"""
参数配置服务
"""
from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.system.model.config import Config
from app.module.system.schema.config import ConfigCreate, ConfigUpdate, ConfigPageQuery
from app.core.redis import get_cache, set_cache, delete_cache, RedisKeyPrefix
from app.core.exceptions import BusinessException, ErrorCode


class ConfigService:
    """参数配置服务"""

    @staticmethod
    async def get_by_id(db: AsyncSession, config_id: int) -> Optional[Config]:
        """根据ID获取配置"""
        result = await db.execute(
            select(Config).where(Config.id == config_id, Config.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_key(db: AsyncSession, key: str) -> Optional[Config]:
        """根据键名获取配置"""
        result = await db.execute(
            select(Config).where(Config.key == key, Config.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_value(db: AsyncSession, key: str, default: str = None) -> Optional[str]:
        """
        获取配置值（优先从缓存获取）

        Args:
            db: 数据库会话
            key: 配置键名
            default: 默认值

        Returns:
            配置值
        """
        # 尝试从缓存获取
        cache_key = f"{RedisKeyPrefix.CONFIG}{key}"
        cached = await get_cache(cache_key)
        if cached is not None:
            return cached

        # 从数据库获取
        config = await ConfigService.get_by_key(db, key)
        if config:
            # 缓存配置值
            await set_cache(cache_key, config.value, expire=3600)
            return config.value

        return default

    @staticmethod
    async def get_list(db: AsyncSession, query: ConfigPageQuery) -> tuple[List[Config], int]:
        """分页查询配置列表"""
        conditions = [Config.deleted == 0]

        if query.category:
            conditions.append(Config.category.like(f"%{query.category}%"))
        if query.name:
            conditions.append(Config.name.like(f"%{query.name}%"))
        if query.key:
            conditions.append(Config.key.like(f"%{query.key}%"))
        if query.type is not None:
            conditions.append(Config.type == query.type)
        if query.visible is not None:
            conditions.append(Config.visible == query.visible)

        # 查询总数
        count_result = await db.execute(
            select(Config).where(and_(*conditions))
        )
        total = len(count_result.all())

        # 分页查询
        result = await db.execute(
            select(Config)
            .where(and_(*conditions))
            .order_by(Config.id.desc())
            .offset(query.offset)
            .limit(query.limit)
        )
        configs = result.scalars().all()

        return list(configs), total

    @staticmethod
    async def create(db: AsyncSession, config_create: ConfigCreate) -> Config:
        """创建配置"""
        # 检查键名是否存在
        existing = await ConfigService.get_by_key(db, config_create.key)
        if existing:
            raise BusinessException(code=ErrorCode.DATA_EXISTS, message="配置键名已存在")

        config = Config(
            category=config_create.category,
            name=config_create.name,
            key=config_create.key,
            value=config_create.value,
            type=config_create.type or 2,
            visible=config_create.visible or 0,
            remark=config_create.remark,
        )

        db.add(config)
        await db.flush()
        await db.refresh(config)

        # 缓存配置
        await set_cache(
            f"{RedisKeyPrefix.CONFIG}{config.key}",
            config.value,
            expire=3600
        )

        return config

    @staticmethod
    async def update(db: AsyncSession, config_id: int, config_update: ConfigUpdate) -> Config:
        """更新配置"""
        config = await ConfigService.get_by_id(db, config_id)
        if not config:
            raise BusinessException(code=ErrorCode.DATA_NOT_EXISTS, message="配置不存在")

        # 更新字段
        update_data = config_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(config, key):
                setattr(config, key, value)

        await db.flush()
        await db.refresh(config)

        # 更新缓存
        await set_cache(
            f"{RedisKeyPrefix.CONFIG}{config.key}",
            config.value,
            expire=3600
        )

        return config

    @staticmethod
    async def delete(db: AsyncSession, config_id: int) -> bool:
        """删除配置"""
        config = await ConfigService.get_by_id(db, config_id)
        if not config:
            raise BusinessException(code=ErrorCode.DATA_NOT_EXISTS, message="配置不存在")

        # 系统配置不允许删除
        if config.type == 1:
            raise BusinessException(code=ErrorCode.PERMISSION_DENIED, message="系统配置不允许删除")

        config.deleted = 1
        await db.flush()

        # 删除缓存
        await delete_cache(f"{RedisKeyPrefix.CONFIG}{config.key}")

        return True