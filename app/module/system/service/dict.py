"""
字典服务
"""
from typing import Optional, List, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.system.model.dict_type import DictType
from app.module.system.model.dict_data import DictData
from app.core.redis import get_cache, set_cache, RedisKeyPrefix
from app.core.exceptions import BusinessException, ErrorCode


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
    async def get_dict_type_page(
        db: AsyncSession,
        page_no: int,
        page_size: int,
        name: Optional[str] = None,
        type: Optional[str] = None,
        status: Optional[int] = None,
    ) -> Tuple[List[DictType], int]:
        """分页查询字典类型"""
        query = select(DictType).where(DictType.deleted == 0)

        if name:
            query = query.where(DictType.name.like(f"%{name}%"))
        if type:
            query = query.where(DictType.type.like(f"%{type}%"))
        if status is not None:
            query = query.where(DictType.status == status)

        # 查询总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        query = query.order_by(DictType.id.desc())
        query = query.offset((page_no - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        types = result.scalars().all()

        return list(types), total

    @staticmethod
    async def get_dict_type_list(
        db: AsyncSession,
        name: Optional[str] = None,
        type: Optional[str] = None,
        status: Optional[int] = None,
    ) -> List[DictType]:
        """获取字典类型列表（不分页，用于导出）"""
        query = select(DictType).where(DictType.deleted == 0)

        if name:
            query = query.where(DictType.name.like(f"%{name}%"))
        if type:
            query = query.where(DictType.type.like(f"%{type}%"))
        if status is not None:
            query = query.where(DictType.status == status)

        query = query.order_by(DictType.id.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_dict_data_export_list(
        db: AsyncSession,
        dict_type: Optional[str] = None,
        label: Optional[str] = None,
        status: Optional[int] = None,
    ) -> List[DictData]:
        """获取字典数据列表（不分页，用于导出）"""
        query = select(DictData).where(DictData.deleted == 0)

        if dict_type:
            query = query.where(DictData.dict_type == dict_type)
        if label:
            query = query.where(DictData.label.like(f"%{label}%"))
        if status is not None:
            query = query.where(DictData.status == status)

        query = query.order_by(DictData.dict_type.desc(), DictData.sort.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_dict_data_by_id(db: AsyncSession, data_id: int) -> Optional[DictData]:
        """根据ID获取字典数据"""
        result = await db.execute(
            select(DictData).where(DictData.id == data_id, DictData.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_dict_data_page(
        db: AsyncSession,
        page_no: int,
        page_size: int,
        dict_type: Optional[str] = None,
        label: Optional[str] = None,
        status: Optional[int] = None,
    ) -> Tuple[List[DictData], int]:
        """分页查询字典数据"""
        query = select(DictData).where(DictData.deleted == 0)

        if dict_type:
            query = query.where(DictData.dict_type == dict_type)
        if label:
            query = query.where(DictData.label.like(f"%{label}%"))
        if status is not None:
            query = query.where(DictData.status == status)

        # 查询总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询（与 Java DictDataMapper.selectPage 一致：按 dictType 降序、sort 降序）
        query = query.order_by(DictData.dict_type.desc(), DictData.sort.desc())
        query = query.offset((page_no - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        data_list = result.scalars().all()

        return list(data_list), total

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

    @staticmethod
    async def get_all_dict_data(db: AsyncSession, status: int = None, dict_type: str = None) -> List[DictData]:
        """
        获取全部字典数据列表

        参考 Java DictDataService.getDictDataList 实现

        Args:
            db: 数据库会话
            status: 状态过滤，None 表示不过滤
            dict_type: 字典类型过滤，None 表示不过滤

        Returns:
            字典数据列表，按 dictType > sort 排序
        """
        query = select(DictData).where(DictData.deleted == 0)
        if status is not None:
            query = query.where(DictData.status == status)
        if dict_type is not None:
            query = query.where(DictData.dict_type == dict_type)
        # 排序：先按 dictType 排序，再按 sort 排序（与 Java 一致）
        query = query.order_by(DictData.dict_type.asc(), DictData.sort.asc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def create_dict_type(
        db: AsyncSession,
        name: str,
        type: str,
        status: int = 0,
        remark: str = None,
    ) -> int:
        """创建字典类型"""
        # 检查类型是否已存在
        existing = await DictService.get_dict_type_by_type(db, type)
        if existing:
            raise BusinessException(code=ErrorCode.DATA_EXISTS, message="字典类型已存在")

        dict_type = DictType(
            name=name,
            type=type,
            status=status,
            remark=remark,
        )
        db.add(dict_type)
        await db.flush()
        await db.refresh(dict_type)
        return dict_type.id

    @staticmethod
    async def update_dict_type(
        db: AsyncSession,
        type_id: int,
        name: Optional[str] = None,
        type: Optional[str] = None,
        status: Optional[int] = None,
        remark: Optional[str] = None,
    ) -> bool:
        """更新字典类型"""
        dict_type = await DictService.get_dict_type_by_id(db, type_id)
        if not dict_type:
            raise BusinessException(code=ErrorCode.DATA_NOT_EXISTS, message="字典类型不存在")

        if name is not None:
            dict_type.name = name
        if type is not None:
            # 检查新类型是否已存在
            existing = await DictService.get_dict_type_by_type(db, type)
            if existing and existing.id != type_id:
                raise BusinessException(code=ErrorCode.DATA_EXISTS, message="字典类型已存在")
            dict_type.type = type
        if status is not None:
            dict_type.status = status
        if remark is not None:
            dict_type.remark = remark

        await db.flush()
        return True

    @staticmethod
    async def delete_dict_type(db: AsyncSession, type_id: int) -> bool:
        """删除字典类型"""
        dict_type = await DictService.get_dict_type_by_id(db, type_id)
        if not dict_type:
            raise BusinessException(code=ErrorCode.DATA_NOT_EXISTS, message="字典类型不存在")

        dict_type.deleted = 1
        await db.flush()
        return True

    @staticmethod
    async def delete_dict_type_list(db: AsyncSession, type_ids: List[int]) -> int:
        """批量删除字典类型"""
        count = 0
        for type_id in type_ids:
            try:
                await DictService.delete_dict_type(db, type_id)
                count += 1
            except BusinessException:
                pass
        return count

    @staticmethod
    async def create_dict_data(
        db: AsyncSession,
        sort: int,
        label: str,
        value: str,
        dict_type: str,
        status: int = 0,
        color_type: str = None,
        css_class: str = None,
        remark: str = None,
    ) -> int:
        """创建字典数据"""
        data = DictData(
            sort=sort,
            label=label,
            value=value,
            dict_type=dict_type,
            status=status,
            color_type=color_type,
            css_class=css_class,
            remark=remark,
        )
        db.add(data)
        await db.flush()
        await db.refresh(data)
        return data.id

    @staticmethod
    async def update_dict_data(
        db: AsyncSession,
        data_id: int,
        sort: Optional[int] = None,
        label: Optional[str] = None,
        value: Optional[str] = None,
        dict_type: Optional[str] = None,
        status: Optional[int] = None,
        color_type: Optional[str] = None,
        css_class: Optional[str] = None,
        remark: Optional[str] = None,
    ) -> bool:
        """更新字典数据"""
        dict_data = await DictService.get_dict_data_by_id(db, data_id)
        if not dict_data:
            raise BusinessException(code=ErrorCode.DATA_NOT_EXISTS, message="字典数据不存在")

        if sort is not None:
            dict_data.sort = sort
        if label is not None:
            dict_data.label = label
        if value is not None:
            dict_data.value = value
        if dict_type is not None:
            dict_data.dict_type = dict_type
        if status is not None:
            dict_data.status = status
        if color_type is not None:
            dict_data.color_type = color_type
        if css_class is not None:
            dict_data.css_class = css_class
        if remark is not None:
            dict_data.remark = remark

        await db.flush()
        return True

    @staticmethod
    async def delete_dict_data(db: AsyncSession, data_id: int) -> bool:
        """删除字典数据"""
        dict_data = await DictService.get_dict_data_by_id(db, data_id)
        if not dict_data:
            raise BusinessException(code=ErrorCode.DATA_NOT_EXISTS, message="字典数据不存在")

        dict_data.deleted = 1
        await db.flush()
        return True

    @staticmethod
    async def delete_dict_data_list(db: AsyncSession, data_ids: List[int]) -> int:
        """批量删除字典数据"""
        count = 0
        for data_id in data_ids:
            try:
                await DictService.delete_dict_data(db, data_id)
                count += 1
            except BusinessException:
                pass
        return count