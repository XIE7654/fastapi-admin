"""
AI 聊天对话服务
参考 ruoyi-vue-pro yudao-module-ai AiChatConversationService
"""
from typing import Optional, List, Tuple, Dict
from datetime import datetime
from sqlalchemy import select, and_, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.module.ai.model.chat_conversation import ChatConversation
from app.module.ai.model.chat_message import ChatMessage
from app.module.ai.schema.chat_conversation import (
    ChatConversationCreate,
    ChatConversationUpdate,
    ChatConversationPageQuery,
)
from app.core.exceptions import BusinessException


class ChatConversationErrorCode:
    """AI 聊天对话错误码定义"""
    CONVERSATION_NOT_EXISTS = 1040030000


class ChatConversationService:
    """AI 聊天对话服务类"""

    @staticmethod
    async def get_by_id(db: AsyncSession, conversation_id: int) -> Optional[ChatConversation]:
        """根据ID获取对话"""
        result = await db.execute(
            select(ChatConversation).where(
                ChatConversation.id == conversation_id,
                ChatConversation.deleted == 0
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_page(
        db: AsyncSession,
        query: ChatConversationPageQuery
    ) -> Tuple[List[ChatConversation], int]:
        """分页查询对话列表"""
        # 构建查询条件
        conditions = [ChatConversation.deleted == 0]

        if query.user_id:
            conditions.append(ChatConversation.user_id == query.user_id)
        if query.title:
            conditions.append(ChatConversation.title.like(f"%{query.title}%"))

        # 查询总数
        count_query = select(func.count()).select_from(ChatConversation).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询，按置顶和时间排序
        result = await db.execute(
            select(ChatConversation)
            .where(and_(*conditions))
            .order_by(
                ChatConversation.pinned.desc(),
                ChatConversation.create_time.desc()
            )
            .offset(query.offset)
            .limit(query.limit)
        )
        conversations = result.scalars().all()

        return list(conversations), total

    @staticmethod
    async def get_list_by_user_id(db: AsyncSession, user_id: int) -> List[ChatConversation]:
        """根据用户ID获取对话列表"""
        result = await db.execute(
            select(ChatConversation)
            .where(
                ChatConversation.user_id == user_id,
                ChatConversation.deleted == 0
            )
            .order_by(
                ChatConversation.pinned.desc(),
                ChatConversation.create_time.desc()
            )
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_message_count_map(
        db: AsyncSession,
        conversation_ids: List[int]
    ) -> Dict[int, int]:
        """获取对话的消息数量映射"""
        if not conversation_ids:
            return {}

        result = await db.execute(
            select(
                ChatMessage.conversation_id,
                func.count(ChatMessage.id).label('count')
            )
            .where(
                ChatMessage.conversation_id.in_(conversation_ids),
                ChatMessage.deleted == 0
            )
            .group_by(ChatMessage.conversation_id)
        )
        return {row.conversation_id: row.count for row in result.all()}

    @staticmethod
    async def create(db: AsyncSession, conversation_create: ChatConversationCreate) -> ChatConversation:
        """创建对话"""
        conversation = ChatConversation(
            user_id=conversation_create.user_id,
            role_id=conversation_create.role_id,
            title=conversation_create.title,
            model_id=conversation_create.model_id,
            model=conversation_create.model,
            system_message=conversation_create.system_message,
            temperature=conversation_create.temperature,
            max_tokens=conversation_create.max_tokens,
            max_contexts=conversation_create.max_contexts,
            pinned=0,
        )

        db.add(conversation)
        await db.flush()
        await db.refresh(conversation)

        return conversation

    @staticmethod
    async def update(
        db: AsyncSession,
        conversation_id: int,
        conversation_update: ChatConversationUpdate
    ) -> ChatConversation:
        """更新对话"""
        conversation = await ChatConversationService.get_by_id(db, conversation_id)
        if not conversation:
            raise BusinessException(
                code=ChatConversationErrorCode.CONVERSATION_NOT_EXISTS,
                message="对话不存在"
            )

        # 更新字段
        update_data = conversation_update.model_dump(exclude_unset=True, exclude={"id"})

        # 处理置顶
        if 'pinned' in update_data and update_data['pinned'] == 1:
            update_data['pinned_time'] = datetime.now()
        elif 'pinned' in update_data and update_data['pinned'] == 0:
            update_data['pinned_time'] = None

        for key, value in update_data.items():
            if hasattr(conversation, key):
                setattr(conversation, key, value)

        await db.flush()
        await db.refresh(conversation)

        return conversation

    @staticmethod
    async def delete(db: AsyncSession, conversation_id: int) -> bool:
        """删除对话（软删除）"""
        conversation = await ChatConversationService.get_by_id(db, conversation_id)
        if not conversation:
            raise BusinessException(
                code=ChatConversationErrorCode.CONVERSATION_NOT_EXISTS,
                message="对话不存在"
            )

        conversation.deleted = 1
        await db.flush()

        return True

    @staticmethod
    async def delete_by_user(db: AsyncSession, conversation_id: int, user_id: int) -> bool:
        """用户删除自己的对话"""
        conversation = await ChatConversationService.get_by_id(db, conversation_id)
        if not conversation:
            raise BusinessException(
                code=ChatConversationErrorCode.CONVERSATION_NOT_EXISTS,
                message="对话不存在"
            )

        if conversation.user_id != user_id:
            raise BusinessException(
                code=ChatConversationErrorCode.CONVERSATION_NOT_EXISTS,
                message="对话不存在"
            )

        conversation.deleted = 1
        await db.flush()

        return True

    @staticmethod
    async def delete_unpinned_by_user(db: AsyncSession, user_id: int) -> int:
        """删除用户未置顶的对话"""
        result = await db.execute(
            update(ChatConversation)
            .where(
                ChatConversation.user_id == user_id,
                ChatConversation.pinned == 0,
                ChatConversation.deleted == 0
            )
            .values(deleted=1)
        )
        await db.flush()
        return result.rowcount