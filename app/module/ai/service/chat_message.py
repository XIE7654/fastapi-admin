"""
AI 聊天消息服务
参考 ruoyi-vue-pro yudao-module-ai AiChatMessageService
"""
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.ai.model.chat_message import ChatMessage
from app.module.ai.schema.chat_message import ChatMessagePageQuery
from app.core.exceptions import BusinessException


class ChatMessageService:
    """AI 聊天消息服务类"""

    @staticmethod
    async def get_by_id(db: AsyncSession, message_id: int) -> Optional[ChatMessage]:
        """根据ID获取消息"""
        result = await db.execute(
            select(ChatMessage).where(ChatMessage.id == message_id, ChatMessage.deleted == 0)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list_by_conversation_id(
        db: AsyncSession,
        conversation_id: int
    ) -> List[ChatMessage]:
        """根据对话ID获取消息列表"""
        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation_id, ChatMessage.deleted == 0)
            .order_by(ChatMessage.id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_page(
        db: AsyncSession,
        query: ChatMessagePageQuery
    ) -> Tuple[List[ChatMessage], int]:
        """分页查询消息列表"""
        # 构建查询条件
        conditions = [ChatMessage.deleted == 0]

        if query.conversation_id:
            conditions.append(ChatMessage.conversation_id == query.conversation_id)
        if query.user_id:
            conditions.append(ChatMessage.user_id == query.user_id)
        if query.content:
            conditions.append(ChatMessage.content.like(f"%{query.content}%"))
        if query.create_time and len(query.create_time) == 2:
            conditions.append(ChatMessage.create_time.between(query.create_time[0], query.create_time[1]))

        # 查询总数
        count_query = select(func.count()).select_from(ChatMessage).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        result = await db.execute(
            select(ChatMessage)
            .where(and_(*conditions))
            .order_by(ChatMessage.id.desc())
            .offset(query.offset)
            .limit(query.limit)
        )
        messages = result.scalars().all()

        return list(messages), total

    @staticmethod
    async def delete(db: AsyncSession, message_id: int) -> bool:
        """删除消息（软删除）"""
        message = await ChatMessageService.get_by_id(db, message_id)
        if not message:
            raise BusinessException(code=404, message="消息不存在")

        message.deleted = 1
        await db.flush()
        return True

    @staticmethod
    async def delete_by_conversation_id(
        db: AsyncSession,
        conversation_id: int
    ) -> bool:
        """删除指定对话的所有消息"""
        result = await db.execute(
            select(ChatMessage).where(
                ChatMessage.conversation_id == conversation_id,
                ChatMessage.deleted == 0
            )
        )
        messages = result.scalars().all()

        for message in messages:
            message.deleted = 1

        await db.flush()
        return True