"""
字典服务
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.system.model.dict_type import DictType
from app.module.system.model.dict_data import DictData
from app.core.redis import get_cache, set_cache, RedisKeyPrefix


class DictService:
    """字典服务"""

    @staticmethod
    async def get_dict_type_by_id(db: AsyncSession, type_id: int) -> Optional[DictType]:
        """根据ID获取字典类型"""
        result = await db.execute(
            select(DictType).where(DictType.id == type_id, DictType.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_dict_type_by_type(db: AsyncSession, dict_type: str) -> Optional[DictType]:
        """根据类型获取字典类型"""
        result = await db.execute(
            select(DictType).where(DictType.type == dict_type, DictType.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_dict_data_list(db: AsyncSession, dict_type: str) -> List[DictData]:
        """
        根据字典类型获取字典数据列表

        优先从缓存获取，缓存不存在则从数据库查询
        """
        # 尝试从缓存获取
        cache_key = f"{RedisKeyPrefix.DICT_DATA}{dict_type}"
        cached = await get_cache(cache_key)
        if cached:
            # TODO: 反序列化缓存数据
            pass

        # 从数据库查询
        result = await db.execute(
            select(DictData)
            .where(DictData.dict_type == dict_type, DictData.deleted == 0, DictData.status == 0)
            .order_by(DictData.sort.asc())
        )
        data_list = list(result.scalars().all())

        # 缓存结果
        if data_list:
            # TODO: 序列化并缓存
            pass

        return data_list

    @staticmethod
    async def get_all_dict_types(db: AsyncSession) -> List[DictType]:
        """获取所有字典类型"""
        result = await db.execute(
            select(DictType)
            .where(DictType.deleted == 0)
            .order_by(DictType.id.asc())
        )
        return list(result.scalars().all())