"""
社交客户端服务
"""
from typing import Optional, List, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.system.model.social import SocialClient, SocialUser


class SocialClientService:
    """社交客户端服务"""

    @staticmethod
    async def get_by_id(db: AsyncSession, client_id: int) -> Optional[SocialClient]:
        """根据ID获取社交客户端"""
        result = await db.execute(
            select(SocialClient).where(SocialClient.id == client_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession) -> List[SocialClient]:
        """获取所有社交客户端"""
        result = await db.execute(
            select(SocialClient).order_by(SocialClient.id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_page(
        db: AsyncSession,
        page_no: int = 1,
        page_size: int = 10,
        name: str = None,
        social_type: int = None,
        user_type: int = None,
        status: int = None,
    ) -> Tuple[List[SocialClient], int]:
        """分页获取社交客户端"""
        conditions = []

        if name:
            conditions.append(SocialClient.name.like(f"%{name}%"))
        if social_type is not None:
            conditions.append(SocialClient.social_type == social_type)
        if user_type is not None:
            conditions.append(SocialClient.user_type == user_type)
        if status is not None:
            conditions.append(SocialClient.status == status)

        # 查询总数
        count_query = select(func.count(SocialClient.id))
        if conditions:
            count_query = count_query.where(*conditions)
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 查询列表
        query = select(SocialClient)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(SocialClient.id.desc())
        query = query.offset((page_no - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total


class SocialUserService:
    """社交用户服务"""

    @staticmethod
    async def get_by_id(db: AsyncSession, social_user_id: int) -> Optional[SocialUser]:
        """根据ID获取社交用户"""
        result = await db.execute(
            select(SocialUser).where(SocialUser.id == social_user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession) -> List[SocialUser]:
        """获取所有社交用户"""
        result = await db.execute(
            select(SocialUser).order_by(SocialUser.id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_page(
        db: AsyncSession,
        page_no: int = 1,
        page_size: int = 10,
        type: int = None,
        openid: str = None,
        nickname: str = None,
    ) -> Tuple[List[SocialUser], int]:
        """分页获取社交用户"""
        conditions = []

        if type is not None:
            conditions.append(SocialUser.type == type)
        if openid:
            conditions.append(SocialUser.openid.like(f"%{openid}%"))
        if nickname:
            conditions.append(SocialUser.nickname.like(f"%{nickname}%"))

        # 查询总数
        count_query = select(func.count(SocialUser.id))
        if conditions:
            count_query = count_query.where(*conditions)
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 查询列表
        query = select(SocialUser)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(SocialUser.id.desc())
        query = query.offset((page_no - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total