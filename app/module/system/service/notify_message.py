"""
站内信消息服务
"""
from typing import List, Optional, Tuple
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.system.model.notify import NotifyMessage
from app.module.system.schema.log import NotifyMessagePageQuery


class NotifyMessageService:
    """站内信消息服务"""

    # 用户类型常量
    USER_TYPE_ADMIN = 1  # 管理后台用户
    USER_TYPE_MEMBER = 2  # 前台会员用户

    @staticmethod
    async def get_unread_count(
        db: AsyncSession,
        user_id: int,
        user_type: int = USER_TYPE_ADMIN
    ) -> int:
        """
        获取用户未读站内信数量

        Args:
            db: 数据库会话
            user_id: 用户ID
            user_type: 用户类型 (1-管理后台用户, 2-前台会员用户)

        Returns:
            未读站内信数量
        """
        result = await db.execute(
            select(func.count(NotifyMessage.id))
            .where(
                NotifyMessage.user_id == user_id,
                NotifyMessage.user_type == user_type,
                NotifyMessage.read_status == 0,  # 未读
            )
        )
        return result.scalar() or 0

    @staticmethod
    async def get_unread_list(
        db: AsyncSession,
        user_id: int,
        user_type: int = USER_TYPE_ADMIN,
        size: int = 10
    ) -> List[NotifyMessage]:
        """
        获取用户未读站内信列表

        Args:
            db: 数据库会话
            user_id: 用户ID
            user_type: 用户类型
            size: 返回数量

        Returns:
            未读站内信列表
        """
        result = await db.execute(
            select(NotifyMessage)
            .where(
                NotifyMessage.user_id == user_id,
                NotifyMessage.user_type == user_type,
                NotifyMessage.read_status == 0,
            )
            .order_by(NotifyMessage.id.desc())
            .limit(size)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, message_id: int) -> Optional[NotifyMessage]:
        """
        根据ID获取站内信

        Args:
            db: 数据库会话
            message_id: 消息ID

        Returns:
            站内信对象
        """
        result = await db.execute(
            select(NotifyMessage).where(NotifyMessage.id == message_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def mark_as_read(
        db: AsyncSession,
        message_ids: List[int],
        user_id: int,
        user_type: int = USER_TYPE_ADMIN
    ) -> int:
        """
        标记站内信为已读

        Args:
            db: 数据库会话
            message_ids: 消息ID列表
            user_id: 用户ID
            user_type: 用户类型

        Returns:
            更新的记录数
        """
        from datetime import datetime

        messages = await db.execute(
            select(NotifyMessage)
            .where(
                NotifyMessage.id.in_(message_ids),
                NotifyMessage.user_id == user_id,
                NotifyMessage.user_type == user_type,
                NotifyMessage.read_status == 0,
            )
        )
        messages_list = list(messages.scalars().all())

        count = 0
        for msg in messages_list:
            msg.read_status = 1
            msg.read_time = datetime.now()
            count += 1

        await db.commit()
        return count

    @staticmethod
    async def mark_all_as_read(
        db: AsyncSession,
        user_id: int,
        user_type: int = USER_TYPE_ADMIN
    ) -> int:
        """
        标记所有站内信为已读

        Args:
            db: 数据库会话
            user_id: 用户ID
            user_type: 用户类型

        Returns:
            更新的记录数
        """
        from datetime import datetime

        messages = await db.execute(
            select(NotifyMessage)
            .where(
                NotifyMessage.user_id == user_id,
                NotifyMessage.user_type == user_type,
                NotifyMessage.read_status == 0,
            )
        )
        messages_list = list(messages.scalars().all())

        count = 0
        for msg in messages_list:
            msg.read_status = 1
            msg.read_time = datetime.now()
            count += 1

        await db.commit()
        return count

    @staticmethod
    async def get_page(db: AsyncSession, query: NotifyMessagePageQuery) -> Tuple[List[NotifyMessage], int]:
        """
        分页查询站内信消息

        Args:
            db: 数据库会话
            query: 分页查询参数

        Returns:
            站内信消息列表和总数
        """
        conditions = []

        if query.user_id:
            conditions.append(NotifyMessage.user_id == query.user_id)
        if query.user_type:
            conditions.append(NotifyMessage.user_type == query.user_type)
        if query.template_code:
            conditions.append(NotifyMessage.template_code == query.template_code)
        if query.template_type:
            conditions.append(NotifyMessage.template_type == query.template_type)
        if query.create_time and len(query.create_time) == 2:
            conditions.append(NotifyMessage.create_time.between(query.create_time[0], query.create_time[1]))

        # 查询总数
        if conditions:
            count_query = select(func.count()).select_from(NotifyMessage).where(and_(*conditions))
        else:
            count_query = select(func.count()).select_from(NotifyMessage)
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        if conditions:
            result = await db.execute(
                select(NotifyMessage)
                .where(and_(*conditions))
                .order_by(NotifyMessage.id.desc())
                .offset(query.offset)
                .limit(query.limit)
            )
        else:
            result = await db.execute(
                select(NotifyMessage)
                .order_by(NotifyMessage.id.desc())
                .offset(query.offset)
                .limit(query.limit)
            )
        messages = result.scalars().all()

        return list(messages), total