"""
OAuth2 客户端服务
"""
from typing import Optional, List, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.system.model.oauth2 import OAuth2Client, OAuth2AccessToken


class OAuth2ClientService:
    """OAuth2 客户端服务"""

    @staticmethod
    async def get_by_id(db: AsyncSession, client_id: int) -> Optional[OAuth2Client]:
        """根据ID获取OAuth2客户端"""
        result = await db.execute(
            select(OAuth2Client).where(OAuth2Client.id == client_id, OAuth2Client.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_client_id(db: AsyncSession, client_id: str) -> Optional[OAuth2Client]:
        """根据客户端编号获取OAuth2客户端"""
        result = await db.execute(
            select(OAuth2Client).where(OAuth2Client.client_id == client_id, OAuth2Client.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession) -> List[OAuth2Client]:
        """获取所有OAuth2客户端"""
        result = await db.execute(
            select(OAuth2Client).where(OAuth2Client.deleted == 0).order_by(OAuth2Client.id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_page(
        db: AsyncSession,
        page_no: int = 1,
        page_size: int = 10,
        name: str = None,
        status: int = None,
    ) -> Tuple[List[OAuth2Client], int]:
        """分页获取OAuth2客户端"""
        conditions = [OAuth2Client.deleted == 0]

        if name:
            conditions.append(OAuth2Client.name.like(f"%{name}%"))
        if status is not None:
            conditions.append(OAuth2Client.status == status)

        # 查询总数
        count_query = select(func.count(OAuth2Client.id))
        if conditions:
            count_query = count_query.where(*conditions)
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 查询列表
        query = select(OAuth2Client)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(OAuth2Client.id.desc())
        query = query.offset((page_no - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total


class OAuth2AccessTokenService:
    """OAuth2 访问令牌服务"""

    @staticmethod
    async def get_by_id(db: AsyncSession, token_id: int) -> Optional[OAuth2AccessToken]:
        """根据ID获取访问令牌"""
        result = await db.execute(
            select(OAuth2AccessToken).where(OAuth2AccessToken.id == token_id, OAuth2AccessToken.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_page(
        db: AsyncSession,
        page_no: int = 1,
        page_size: int = 10,
        user_id: int = None,
        user_type: int = None,
        client_id: str = None,
    ) -> Tuple[List[OAuth2AccessToken], int]:
        """分页获取访问令牌"""
        from datetime import datetime

        conditions = [OAuth2AccessToken.deleted == 0]

        if user_id is not None:
            conditions.append(OAuth2AccessToken.user_id == user_id)
        if user_type is not None:
            conditions.append(OAuth2AccessToken.user_type == user_type)
        if client_id:
            conditions.append(OAuth2AccessToken.client_id == client_id)

        # 只返回未过期的
        conditions.append(OAuth2AccessToken.expires_time > datetime.now())

        # 查询总数
        count_query = select(func.count(OAuth2AccessToken.id))
        if conditions:
            count_query = count_query.where(*conditions)
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 查询列表
        query = select(OAuth2AccessToken)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(OAuth2AccessToken.id.desc())
        query = query.offset((page_no - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total